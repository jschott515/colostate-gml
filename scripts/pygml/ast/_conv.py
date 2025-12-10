import typing

from ._types import *


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


def convert(data: typing.MutableMapping):
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
        if len(data["inner"]) == 2:
            return convert(data["inner"][1])  # FIXME bad assumption
        else:
            return Expr(
                ELet(
                    "fa",
                    None,
                    convert(data["inner"][0]),  # Handle Task
                    Expr(
                        ELet(
                            data["inner"][1]["inner"][0]["referencedDecl"]["name"],
                            None,
                            convert(data["inner"][1]["inner"][1]),  # to CallExpr
                            Expr(
                                ELet(
                                    "a",
                                    None,
                                    convert(data["inner"][2]),  # to OmpTaskWait
                                    convert(data["inner"][3]),  # to BinaryOperator - assign result
                                )
                            )
                        )
                    )
                )
            )
    if kind == "IfStmt":
        assert len(data["inner"]) == 3, "requires if/then/else expressions"
        return Expr(
            EIf(
                convert(data["inner"][0]),
                convert(data["inner"][1]),
                convert(data["inner"][2]),
            )
        )
    if kind == "ImplicitCastExpr":
        return convert(data["inner"][0])
    if kind == "DeclRefExpr":
        return Expr(EVar(Id(data["referencedDecl"]["name"])))
    if kind == "BinaryOperator":
        op = data["opcode"]
        if op == "=":
            pass # FIXME
        return Expr(
            EInfixop(
                CONVERT_OPCODE[op].value,
                convert(data["inner"][0]),
                convert(data["inner"][1]),
            )   
        )
    if kind == "OMPTaskDirective":
        return Expr(
            EFuture(
                None,
                convert(data["inner"][2]["inner"][0]["inner"][0]["inner"][1])  # to CallExpr
            )
        )
    if kind == "OMPTaskwaitDirective":
        return Expr(
            EForce(
                Expr(
                    EVar(Id("fa"))  # FIXME
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
