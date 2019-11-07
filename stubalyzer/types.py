from typing import Union

from mypy.nodes import (
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

"""
SymbolNodes that are interesting for stub files.
Excludes MypyFiles (the modules themselves), imported names and Mypy placeholders
"""
