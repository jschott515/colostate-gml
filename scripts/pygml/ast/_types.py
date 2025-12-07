from __future__ import annotations
import dataclasses
import enum
import typing


"""
LONG IDENTIFIERS
"""

@dataclasses.dataclass
class Id:
    name: str


@dataclasses.dataclass
class ModId:
    module: str
    rest: LongId


LongId = typing.Union[Id, ModId]


"""
CONSTANTS
"""

@dataclasses.dataclass
class Num:
    value: int


@dataclasses.dataclass
class String:
    value: str


@dataclasses.dataclass
class Char:
    value: str


@dataclasses.dataclass
class Bool:
    value: bool


@dataclasses.dataclass
class Unit:
    pass


@dataclasses.dataclass
class Futref:
    value: object


Const = typing.Union[Num, String, Char, Bool, Unit, Futref]


"""
INFIX OPERATORS
"""

class InfixOp(enum.StrEnum):
    Plus = "Plus"
    Minus = "Minus"
    Times = "Times"
    Div = "Div"
    Lt = "Lt"
    Le = "Le"
    Gt = "Gt"
    Ge = "Ge"
    Eq = "Eq"
    Ne = "Ne"
    And = "And"
    Or = "Or"
    Concat = "Concat"


"""
EXPRESSION DESCRIPTION
"""

class IsRecursive(enum.StrEnum):
    Recursive = "Recursive"
    Terminal = "Terminal"


@dataclasses.dataclass
class EVar:
    id: LongId


@dataclasses.dataclass
class EConst:
    value: Const


@dataclasses.dataclass
class EInfixop:
    op: str
    left: Expr
    right: Expr


@dataclasses.dataclass
class EFunc:
    recursive: typing.Optional[str]
    name: str
    arg: str
    arg_ty: typing.Optional[object]
    ret_ty: typing.Optional[object]
    uf: typing.Optional[object]
    ut: typing.Optional[object]
    body: Expr


@dataclasses.dataclass
class EIf:
    cond: Expr
    then: Expr
    els: Expr


@dataclasses.dataclass
class ELet:
    name: str
    ann: typing.Optional[object]
    value: Expr
    body: Expr


@dataclasses.dataclass
class ELetTuple:
    names: typing.List[str]
    value: Expr
    body: Expr


@dataclasses.dataclass
class ELetRecord:
    fields: typing.List[tuple]
    value: Expr
    body: Expr


@dataclasses.dataclass
class EApp:
    fn: Expr
    v1: typing.Optional[object]
    v2: typing.Optional[object]
    arg: Expr


@dataclasses.dataclass
class EMatch:
    scrutinee: Expr
    cases: typing.List[tuple]


@dataclasses.dataclass
class ETuple:
    items: typing.List[Expr]


@dataclasses.dataclass
class ERef:
    expr: Expr


@dataclasses.dataclass
class EDeref:
    expr: Expr


@dataclasses.dataclass
class EUpdate:
    target: Expr
    value: Expr


@dataclasses.dataclass
class EFuture:
    v: typing.Optional[object]
    expr: Expr


@dataclasses.dataclass
class EForce:
    expr: Expr


@dataclasses.dataclass
class EPar:
    left: Expr
    right: Expr


@dataclasses.dataclass
class ETry:
    expr: Expr
    cases: typing.List[tuple]


@dataclasses.dataclass
class EAnnot:
    expr: Expr
    typ: object


@dataclasses.dataclass
class ENewVert:
    var: object
    typ: object
    expr: Expr


"""
EXPRESSION WRAPPER
"""

@dataclasses.dataclass
class Expr:
    edesc: ExprDesc
    eloc: typing.Optional[object] = None
    etyp: typing.Optional[object] = None
    egr: typing.Optional[object] = None


ExprDesc = typing.Union[
    EVar, EConst, EInfixop, EFunc, EIf,
    ELet, ELetTuple, ELetRecord,
    EApp, EMatch, ETuple,
    ERef, EDeref, EUpdate,
    EFuture, EForce, EPar,
    ETry, EAnnot, ENewVert
]


"""
DECLARATIONS
"""

@dataclasses.dataclass
class DVal:
    name: str
    typ: typing.Optional[object]
    expr: Expr


@dataclasses.dataclass
class DExp:
    expr: Expr


@dataclasses.dataclass
class DExtType:
    name: str


@dataclasses.dataclass
class DExtRecType:
    name: str
    fields: typing.List[typing.Tuple[LongId, object]]


@dataclasses.dataclass
class DExternal:
    id: LongId
    typ: object


@dataclasses.dataclass
class DTypeDef:
    params: typing.List[str]
    name: str
    constructors: typing.List[tuple]


DeclDesc = typing.Union[
    DVal,
    DExp,
    DExtType,
    DExtRecType,
    DExternal,
    DTypeDef
]


"""
DECLARATION WRAPPER
"""

@dataclasses.dataclass
class Decl:
    ddesc: DeclDesc
    dloc: typing.Optional[object] = None
    dinfo: typing.Optional[object] = None


"""
PROGRAM
"""

Prog = typing.List[Decl]
