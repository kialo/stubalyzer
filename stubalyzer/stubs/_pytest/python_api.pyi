from types import TracebackType
from typing import Any, Generic, Optional, Pattern, Tuple, Type, TypeVar, Union

from ._code import ExceptionInfo

_E = TypeVar("_E", bound=BaseException)

def raises(
    expected_exception: Union[Type[_E], Tuple[Type[_E], ...]],
    *,
    match: Optional[Union[str, Pattern]] = ...
) -> RaisesContext[_E]: ...

class RaisesContext(Generic[_E]):
    expected_exception: Any = ...
    message: Any = ...
    match_expr: Any = ...
    excinfo: Any = ...
    def __init__(
        self,
        expected_exception: Union[Type[_E], Tuple[Type[_E], ...]],
        message: str,
        match_expr: Optional[Union[str, Pattern]] = ...,
    ) -> None: ...
    def __enter__(self) -> ExceptionInfo[_E]: ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool: ...
