from typing import overload

def matching(foo: int, bar: str) -> str: ...
def additional_args(foo: int, bar: int) -> str: ...
def additional_optional_args(foo: int, bar: int = 0) -> str: ...
@overload
def overloaded_additional_args(foo: str, bar: str) -> str: ...
@overload
def overloaded_additional_args(foo: int, bar: int) -> int: ...
@overload
def overloaded_additional_optional_args(foo: str, bar: str = "overloaded") -> str: ...
@overload
def overloaded_additional_optional_args(foo: int, bar: int = 0) -> int: ...