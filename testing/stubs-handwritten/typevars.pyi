from typing import Any, Callable, List, Tuple, TypeVar

PlainTypeVar = TypeVar("PlainTypeVar")
BoundTypeVar = TypeVar("BoundTypeVar", bound=Callable[..., Any])
BoundTypeVarMoreSpecific = TypeVar("BoundTypeVarMoreSpecific", bound=Callable[[], int])
ValuesTypeVar = TypeVar("ValuesTypeVar", str, int, bool)
ValuesTypeVarWrongOrder = TypeVar("ValuesTypeVarWrongOrder", int, str, bool)
ValuesTypeVarNoValuesInGenerated = TypeVar(
    "ValuesTypeVarNoValuesInGenerated", int, str, bool
)
ValuesTypeVarMoreSpecific = TypeVar(
    "ValuesTypeVarMoreSpecific", List[int], Tuple[int, ...]
)
