from typing import Any, overload

from .decorators import identity_decorator

def matching(foo: int, bar: str) -> str: ...
def additional_args(foo: int, bar: int) -> str: ...
def additional_optional_args(foo: int, bar: int = 0) -> str: ...
def matching_with_arg_star(foo: int, bar: str, *args: int) -> str: ...
def matching_with_missing_arg_star(foo: Any, bar: Any) -> Any: ...
def mismatching_with_arg_star(foo: int, *args: Any): ...
def mismatching_with_additional_arg_star(foo: int, *args: str): ...
def matching_with_kwarg_star2(foo: int, bar: str, **kwargs: int) -> str: ...
def matching_with_missing_kwarg_star2(foo: Any, bar: Any) -> Any: ...
def mismatching_with_kwarg_star2(foo: int, **kwargs: Any): ...
def mismatching_with_additional_kwarg_star2(foo: int, **kwargs: str): ...
def missing_function(foo:int, bar:int) -> int: ...
@overload
def overloaded_additional_args(foo: str, bar: str) -> str: ...
@overload
def overloaded_additional_args(foo: int, bar: int) -> int: ...
@overload
def overloaded_additional_optional_args(foo: str, bar: str = "overloaded") -> str: ...
@overload
def overloaded_additional_optional_args(foo: int, bar: int = 0) -> int: ...
@identity_decorator
def decorated_function(foo: str) -> str: ...
@identity_decorator
def decorated_with_additional_args(foo: int, bar: str) -> str: ...
@identity_decorator
def decorated_with_additional_optional_args(foo: int, bar: int = 0) -> str: ...
