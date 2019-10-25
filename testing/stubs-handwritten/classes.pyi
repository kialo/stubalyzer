from typing import Any

class SuperWithMethod:
    def super_method(self, foo: int) -> str: ...

class SubclassWithMethod(SuperWithMethod):
    def sub_method(self, bar: str) -> int: ...

class SuperWithClassmethod:
    @classmethod
    def super_classmethod(cls, bar: str) -> int: ...

class SubclassWithClassmethod(SuperWithClassmethod): ...

class SuperWithOverridableMethod:
    def overwritten(self, bar: str, foo: int) -> str: ...

class OverridingMethod(SuperWithOverridableMethod):
    def overwritten(self, bar: str, foo: int) -> str: ...

class SuperWithOverridableClassmethod:
    @classmethod
    def overwritten(cls, bar: str, foo: int) -> SuperWithOverridableClassmethod: ...

class OverridingClassmethod(SuperWithOverridableClassmethod):
    @classmethod
    def overwritten(cls, bar: str, foo: int) -> OverridingClassmethod: ...

class ClassWithInvalidCustomStub:
    def argument_order_wrong(self, bar: str, foo: int) -> int: ...
    def argument_names_wrong(self, foor: int, bart: str) -> str: ...
    def argument_types_wrong(self, foo: bool, bar: str) -> bool: ...
    def argument_types_less_specific(self, foo: Any, bar: Any) -> Any: ...
    def return_type_less_specific(self, foo: int, bar: str) -> Any: ...
    def return_type_wrong(self, foo: int, bar: str) -> str: ...
