from typing import Union

from mypy.nodes import (
    ARG_NAMED,
    ARG_NAMED_OPT,
    ARG_OPT,
    ARG_POS,
    Decorator,
    FuncDef,
    OverloadedFuncDef,
    TypeAlias,
    TypeInfo,
    TypeVarExpr,
    Var,
)

RelevantSymbolNode = Union[
    Decorator, FuncDef, OverloadedFuncDef, Var, TypeInfo, TypeVarExpr, TypeAlias
]

STRICT_ARG_KINDS = [ARG_POS, ARG_OPT, ARG_NAMED, ARG_NAMED_OPT]

"""
SymbolNodes that are interesting for stub files.
Excludes MypyFiles (the modules themselves), imported names and Mypy placeholders
"""
