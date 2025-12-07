import typing

from ._types import *


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def make_const(node: typing.Dict) -> Expr:
    kind = node["kind"]

    if kind == "IntegerLiteral":
        return Expr(EConst(Num(int(node["value"]))))
    if kind == "StringLiteral":
        return Expr(EConst(String(node["value"])))
    if kind == "CharacterLiteral":
        return Expr(EConst(Char(node["value"])))
    if kind == "CXXBoolLiteralExpr":
        return Expr(EConst(Bool(node["value"])))

    raise NotImplementedError(f"constant kind {kind}")

def make_id(name: str):
    return Id(name)

OPERATOR_MAP = {
    "+": InfixOp.Plus,
    "Add": InfixOp.Plus,

    "-": InfixOp.Minus,
    "Sub": InfixOp.Minus,

    "*": InfixOp.Times,
    "Mul": InfixOp.Times,

    "/": InfixOp.Div,
    "Div": InfixOp.Div,

    "<": InfixOp.Lt,
    "Less": InfixOp.Lt,

    "<=": InfixOp.Le,
    "LessEqual": InfixOp.Le,

    ">": InfixOp.Gt,
    "Greater": InfixOp.Gt,

    ">=": InfixOp.Ge,
    "GreaterEqual": InfixOp.Ge,

    "==": InfixOp.Eq,
    "Equal": InfixOp.Eq,

    "!=": InfixOp.Ne,
    "NotEqual": InfixOp.Ne,

    "&&": InfixOp.And,
    "LAnd": InfixOp.And,

    "||": InfixOp.Or,
    "LOr": InfixOp.Or,

    "^": InfixOp.Concat,
}

def convert_op(op_str):
    op = OPERATOR_MAP.get(op_str)
    if op is None:
        return None
    return op.name

# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------

def safe(node, default):
    """Return node if dict, else default."""
    return node if isinstance(node, dict) else default


def inner_list(node):
    x = node.get("inner") if isinstance(node, dict) else None
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


# ------------------------------------------------------------
# main expression dispatcher
# ------------------------------------------------------------

def convert_expr(node):

    if not isinstance(node, dict):
        return Expr(Unhandled("non-dict", node))

    kind = node.get("kind", "<missing>")

    # literals
    if kind.endswith("Literal"):
        return make_const(node)

    # variable reference
    if kind == "DeclRefExpr":
        return Expr(EVar(Id(node["referencedDecl"]["name"])))

    # operators
    if kind == "BinaryOperator":
        lhs = convert_expr(node["inner"][0])
        rhs = convert_expr(node["inner"][1])
        return Expr(EInfixop(convert_op(node["opcode"]), lhs, rhs))

    # unwrap casts
    if kind == "ImplicitCastExpr":
        return convert_expr(node["inner"][0])

    # function call
    if kind == "CallExpr":
        fn = convert_expr(node["inner"][0])
        arg = convert_expr(node["inner"][1]) if len(node["inner"]) > 1 else None
        return Expr(EApp(fn, None, None, arg))

    if kind == "DeclStmt":
        return None

    # if expressions
    if kind == "IfStmt":
        cond = convert_expr(node["inner"][0])
        then = convert_expr(node["inner"][1])
        els = convert_expr(node["inner"][2]) if len(node["inner"]) > 2 else None
        return Expr(EIf(cond, then, els))

    # OpenMP futures
    if kind == "OMPTaskDirective":
        expr = convert_expr(inner_list(node)[0]["inner"][0])
        return Expr(EFuture(None, expr))

    if kind == "OMPTaskwaitDirective":
        return Expr(EForce(Expr(EVar(Id("taskwait")))))

    # statements we collapse
    if kind == "ReturnStmt":
        return convert_expr(inner_list(node)[0])

    if kind == "CompoundStmt":
        return collapse_block(node)

    # anything else
    return Expr(Unhandled(kind, node))


# ------------------------------------------------------------
# collapse a compound block
# ------------------------------------------------------------

def collapse_block(node):
    items = inner_list(node)

    acc = Expr(Unit())   # default empty block → ()
    for s in reversed(items):
        e = convert_expr(s)
        acc = Expr(ELet("_", None, e, acc))

    return acc


# ------------------------------------------------------------
# declaration dispatcher
# ------------------------------------------------------------

def convert_decl(node):
    if not isinstance(node, dict):
        return Decl(Unhandled("non-dict-decl", node))

    kind = node.get("kind")

    if kind == "FunctionDecl":
        return convert_function(node)

    return Decl(Unhandled(kind, node))


def convert_function(node):
    name = node["name"]

    params = inner_list(node)
    body = convert_expr(params[-1])
    arg = params[0]["name"]

    fn = Expr(EFunc("Recursive",
                    name,
                    arg,
                    None,None,None,None,
                    body))

    return Decl(DVal(name, None, fn))


# ------------------------------------------------------------
# program
# ------------------------------------------------------------

def convert_program(ast):
    if isinstance(ast, dict):
        return [convert_decl(ast)]
    if isinstance(ast, list):
        return [convert_decl(n) for n in ast]
    return [Decl(Unhandled("program", ast))]
