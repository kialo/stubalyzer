from typing import Any, Callable, List, Tuple, TypeVar

PlainTypeVar = TypeVar("PlainTypeVar")
BoundTypeVar = TypeVar("BoundTypeVar", bound=Callable[..., Any])
BoundTypeVarMoreSpecific = TypeVar("BoundTypeVarMoreSpecific", bound=Callable[..., Any])
ValuesTypeVar = TypeVar("ValuesTypeVar", str, int, bool)
ValuesTypeVarWrongOrder = TypeVar("ValuesTypeVarWrongOrder", str, int, bool)
ValuesTypeVarNoValuesInGenerated = TypeVar("ValuesTypeVarNoValuesInGenerated")
ValuesTypeVarMoreSpecific = TypeVar("ValuesTypeVarMoreSpecific", List, Tuple)
