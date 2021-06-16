from typing import Any, Callable, Optional, TypeVar, overload

_C = TypeVar("_C", bound=Callable[..., Any])

@overload
def fixture(callable_or_scope: _C) -> _C: ...
@overload
def fixture(
    callable_or_scope: Optional[Any] = ...,
    *args: Any,
    scope: str = ...,
    params: Optional[Any] = ...,
    autouse: bool = ...,
    ids: Optional[Any] = ...,
    name: Optional[Any] = ...
) -> Callable[[_C], _C]: ...
