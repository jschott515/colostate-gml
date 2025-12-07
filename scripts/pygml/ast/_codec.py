from ._types import *


"""
LONG IDENTIFIERS
"""

def decode_longid(data) -> LongId:
    tag = data[0]
    if tag == "Id":
        return Id(data[1])
    elif tag == "Modid":
        return ModId(data[1], decode_longid(data[2]))
    else:
        raise ValueError("bad longid", data)


def encode_longid(x):
    if isinstance(x, Id):
        return ["Id", x.name]
    if isinstance(x, ModId):
        return ["Modid", x.module, encode_longid(x.rest)]
    raise TypeError(x)


"""
CONSTANTS
"""

def decode_const(data):
    tag = data[0]
    if tag == "Num":
        return Num(data[1])
    raise ValueError("bad const", data)


def encode_const(c):
    if isinstance(c, Num):
        return ["Num", c.value]
    raise TypeError(c)


"""
EXPRESSIONS
"""

def decode_expr(data) -> Expr:
    edesc = data["edesc"]
    tag = edesc[0]

    def E(x):
        return decode_expr(x)

    # --------------------------------------------------
    # Basic
    # --------------------------------------------------
    if tag == "EVar":
        node = EVar(decode_longid(edesc[1]))

    elif tag == "EConst":
        node = EConst(decode_const(edesc[1]))

    elif tag == "EInfixop":
        node = EInfixop(
            edesc[1][0],
            E(edesc[2]),
            E(edesc[3])
        )

    # --------------------------------------------------
    # Functions & flow
    # --------------------------------------------------
    elif tag == "EFunc":
        node = EFunc(
            edesc[1][0] if edesc[1] else None,
            edesc[2],
            edesc[3],
            edesc[4],
            edesc[5],
            edesc[6],
            edesc[7],
            E(edesc[8])
        )

    elif tag == "EIf":
        node = EIf(E(edesc[1]), E(edesc[2]), E(edesc[3]))

    elif tag == "ELet":
        node = ELet(
            edesc[1],
            edesc[2],
            E(edesc[3]),
            E(edesc[4])
        )

    elif tag == "ELetTuple":
        node = ELetTuple(
            edesc[1],          # tuple pattern
            edesc[2],          # annotation
            E(edesc[3]),      # bound expression
            E(edesc[4])       # body
        )

    elif tag == "ELetRecord":
        node = ELetRecord(
            edesc[1],          # fields
            edesc[2],          # annotation
            E(edesc[3]),      # expr
            E(edesc[4])       # body
        )

    # --------------------------------------------------
    # Application
    # --------------------------------------------------
    elif tag == "EApp":
        node = EApp(
            E(edesc[1]),
            edesc[2],
            edesc[3],
            E(edesc[4])
        )

    # --------------------------------------------------
    # Matching
    # --------------------------------------------------
    elif tag == "EMatch":
        node = EMatch(
            E(edesc[1]),
            [(pat, E(rhs)) for pat, rhs in edesc[2]]
        )

    # --------------------------------------------------
    # Data
    # --------------------------------------------------
    elif tag == "ETuple":
        node = ETuple([E(x) for x in edesc[1]])

    elif tag == "ERef":
        node = ERef(E(edesc[1]))

    elif tag == "EDeref":
        node = EDeref(E(edesc[1]))

    elif tag == "EUpdate":
        node = EUpdate(
            E(edesc[1]),
            E(edesc[2])
        )

    # --------------------------------------------------
    # Concurrency / effects
    # --------------------------------------------------
    elif tag == "EFuture":
        node = EFuture(edesc[1], E(edesc[2]))

    elif tag == "EForce":
        node = EForce(E(edesc[1]))

    # --------------------------------------------------
    # Other
    # --------------------------------------------------
    elif tag == "EPar":
        node = EPar([E(x) for x in edesc[1]])

    elif tag == "ETry":
        node = ETry(
            E(edesc[1]),
            E(edesc[2])
        )

    elif tag == "EAnnot":
        node = EAnnot(
            E(edesc[1]),
            edesc[2]
        )

    elif tag == "ENewVert":
        node = ENewVert(E(edesc[1]))

    else:
        raise ValueError("unknown expr tag", tag)

    return Expr(
        node,
        data.get("eloc"),
        data.get("etyp"),
        data.get("egr")
    )


def encode_expr(e: Expr):
    d = e.edesc

    # Basic
    if isinstance(d, EVar):
        ed = ["EVar", encode_longid(d.id)]

    elif isinstance(d, EConst):
        ed = ["EConst", encode_const(d.value)]

    elif isinstance(d, EInfixop):
        ed = ["EInfixop", [d.op], encode_expr(d.left), encode_expr(d.right)]

    # Functions & flow
    elif isinstance(d, EFunc):
        ed = [
            "EFunc",
            [d.recursive] if d.recursive else None,
            d.name,
            d.arg,
            d.arg_ty,
            d.ret_ty,
            d.uf,
            d.ut,
            encode_expr(d.body)
        ]

    elif isinstance(d, EIf):
        ed = ["EIf",
            encode_expr(d.cond),
            encode_expr(d.then),
            encode_expr(d.els)
        ]

    elif isinstance(d, ELet):
        ed = ["ELet",
            d.name,
            d.ann,
            encode_expr(d.value),
            encode_expr(d.body)
        ]

    elif isinstance(d, ELetTuple):
        ed = ["ELetTuple",
            d.pat,
            d.ann,
            encode_expr(d.value),
            encode_expr(d.body)
        ]

    elif isinstance(d, ELetRecord):
        ed = ["ELetRecord",
            d.fields,
            d.ann,
            encode_expr(d.value),
            encode_expr(d.body)
        ]

    # App
    elif isinstance(d, EApp):
        ed = ["EApp",
            encode_expr(d.fn),
            d.v1,
            d.v2,
            encode_expr(d.arg)
        ]

    # Match
    elif isinstance(d, EMatch):
        ed = ["EMatch",
            encode_expr(d.scrutinee),
            [(pat, encode_expr(rhs)) for pat, rhs in d.cases]
        ]

    # Data
    elif isinstance(d, ETuple):
        ed = ["ETuple", [encode_expr(x) for x in d.values]]

    elif isinstance(d, ERef):
        ed = ["ERef", encode_expr(d.value)]

    elif isinstance(d, EDeref):
        ed = ["EDeref", encode_expr(d.value)]

    elif isinstance(d, EUpdate):
        ed = ["EUpdate",
            encode_expr(d.target),
            encode_expr(d.value)
        ]

    # Effects
    elif isinstance(d, EFuture):
        ed = ["EFuture", d.v, encode_expr(d.expr)]

    elif isinstance(d, EForce):
        ed = ["EForce", encode_expr(d.expr)]

    # Other
    elif isinstance(d, EPar):
        ed = ["EPar", [encode_expr(x) for x in d.values]]

    elif isinstance(d, ETry):
        ed = ["ETry",
            encode_expr(d.try_expr),
            encode_expr(d.catch_expr)
        ]

    elif isinstance(d, EAnnot):
        ed = ["EAnnot",
            encode_expr(d.expr),
            d.ann
        ]

    elif isinstance(d, ENewVert):
        ed = ["ENewVert", encode_expr(d.expr)]

    else:
        raise TypeError("unhandled expr", d)

    return {
        "edesc": ed,
        "eloc": e.eloc,
        "etyp": e.etyp,
        "egr": e.egr
    }


"""
DECLARATIONS
"""

def decode_decl(data) -> Decl:
    desc = data["ddesc"]
    tag = desc[0]

    if tag == "DVal":
        node = DVal(
            desc[1],
            desc[2],
            decode_expr(desc[3])
        )

    elif tag == "DExp":
        node = DExp(
            decode_expr(desc[1])
        )

    elif tag == "DExtType":
        node = DExtType(desc[1])

    elif tag == "DExtRecType":
        # desc[2] is list[(longid, typ)]
        fields = [
            (decode_longid(fid), ftyp)
            for (fid, ftyp) in desc[2]
        ]
        node = DExtRecType(desc[1], fields)

    elif tag == "DExternal":
        node = DExternal(
            decode_longid(desc[1]),
            desc[2]
        )

    elif tag == "DTypeDef":
        node = DTypeDef(
            desc[1],   # params : list[str]
            desc[2],   # type name
            desc[3]    # constructors
        )

    else:
        raise ValueError("unsupported decl", tag)

    return Decl(
        node,
        data.get("dloc"),
        data.get("dinfo")
    )


def encode_decl(d: Decl):
    desc = d.ddesc

    if isinstance(desc, DVal):
        dd = [
            "DVal",
            desc.name,
            desc.typ,
            encode_expr(desc.expr)
        ]

    elif isinstance(desc, DExp):
        dd = [
            "DExp",
            encode_expr(desc.expr)
        ]

    elif isinstance(desc, DExtType):
        dd = [
            "DExtType",
            desc.name
        ]

    elif isinstance(desc, DExtRecType):
        dd = [
            "DExtRecType",
            desc.name,
            [
                (encode_longid(fid), ftyp)
                for (fid, ftyp) in desc.fields
            ]
        ]

    elif isinstance(desc, DExternal):
        dd = [
            "DExternal",
            encode_longid(desc.id),
            desc.typ
        ]

    elif isinstance(desc, DTypeDef):
        dd = [
            "DTypeDef",
            desc.params,
            desc.name,
            desc.ctors
        ]

    else:
        raise TypeError("unhandled decl", desc)

    return {
        "ddesc": dd,
        "dloc": d.dloc,
        "dinfo": d.dinfo
    }


"""
PROGRAM
"""

def decode_program(js) -> typing.List[Decl]:
    return [decode_decl(d) for d in js]


def encode_program(prog):
    return [encode_decl(d) for d in prog]
