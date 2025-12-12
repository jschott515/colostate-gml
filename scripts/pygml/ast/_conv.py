import typing

from ._types import *


class Task:
    def __init__(self, name: str) -> None:
        self.name = name
        self.captured_decl: EVar = None

    def set_captured_decl(self, expr: Expr):
        edesc = expr.edesc
        assert isinstance(edesc, EVar)
        self.captured_decl = edesc

active_task: Task | None = None

CONVERT_OPCODE = {
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


def collapse(data):
    global active_task
    assert data["kind"] == "CompoundStmt"
    if len(data["inner"]) == 1:
        return convert(data["inner"][0])
    else:
        node = data["inner"].pop(0)
        if node["kind"] == "OMPTaskDirective":
            active_task = Task("fa")
            return Expr(
                ELet(
                    active_task.name,
                    None,
                    convert(node),
                    collapse(data),
                )
            )
        if node["kind"] == "BinaryOperator":
            op = node["opcode"]
            assert op == "="
            decl, assignment = node["inner"]
            return Expr(
                ELet(
                    decl["referencedDecl"]["name"],
                    None,
                    convert(assignment),
                    collapse(data),
                )
            )
        if node["kind"] == "OMPTaskwaitDirective":
            return Expr(
                ELet(
                    active_task.captured_decl.id.name,
                    None,
                    convert(node),
                    collapse(data),
                )
            )
        return Expr(
            ELet(
                "_",
                None,
                convert(node),
                collapse(data),
            )
        )


def convert(data: typing.MutableMapping):
    global active_task
    kind = data["kind"]

    if kind == "IntegerLiteral":
        return Expr(EConst(Num(int(data["value"]))))
    if kind == "StringLiteral":
        return Expr(EConst(String(data["value"])))
    if kind == "CharacterLiteral":
        return Expr(EConst(Char(data["value"])))
    if kind == "CXXBoolLiteralExpr":
        return Expr(EConst(Bool(data["value"])))

    if kind == "FunctionDecl":
        name = data["name"]
        return Decl(
            DVal(
                name,
                None,
                Expr(
                    EFunc(
                        'Recursive',
                        name,
                        data["inner"][0]["name"],
                        None, None, None, None,
                        convert(data["inner"][1]),
                    )
                )
            )
        )
    if kind == "CompoundStmt":
        data["inner"] = [node for node in data["inner"] if node["kind"] != "DeclStmt"]
        return collapse(data)
    if kind == "IfStmt":
        return Expr(
            EIf(
                convert(data["inner"][0]),
                convert(data["inner"][1]),
                None if not data.get("hasElse", False) else convert(data["inner"][2]),
            )
        )
    if kind == "ImplicitCastExpr":
        return convert(data["inner"][0])
    if kind == "DeclRefExpr":
        return Expr(EVar(Id(data["referencedDecl"]["name"])))
    if kind == "BinaryOperator":
        op = data["opcode"]
        if op == "=":
            raise ValueError
        return Expr(
            EInfixop(
                CONVERT_OPCODE[op].value,
                convert(data["inner"][0]),
                convert(data["inner"][1]),
            )   
        )
    if kind == "OMPTaskDirective":
        captured_stmt = data["inner"][-1]
        var_decl, body = captured_stmt["inner"][0]["inner"][0]["inner"]
        active_task.set_captured_decl(convert(var_decl))
        return Expr(
            EFuture(
                None,
                convert(body)
            )
        )
    if kind == "OMPTaskwaitDirective":
        task_name = active_task.name
        active_task = None
        return Expr(
            EForce(
                Expr(
                    EVar(Id(task_name))
                )
            )
        )
    if kind == "CallExpr":
        return Expr(
            EApp(
                convert(data["inner"][0]),
                None,
                None,
                convert(data["inner"][1]),
            )
        )
    if kind == "ReturnStmt":
        return convert(data["inner"][0])
    raise ValueError(kind)


def convert_program(data: typing.MutableMapping):
    return [convert(data)]
