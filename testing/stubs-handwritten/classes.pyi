from typing import Any

class AClass:
    def a_method(self, foo: int) -> str: ...
    @classmethod
    def a_classmethod(cls, bar: str) -> int: ...

class AnotherClass: ...

class ClassWithoutSuperClassInHandwritten:
    """Instead of subclassing "AClass" this class defines the method directly.

    This is expected to give us a MISLOCATED_SYMBOL result."""

    def a_method(self, foo: int) -> str: ...

class SubClassOfAClass(AClass): ...
class MissingClass: ...

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
    def argument_types_wrong(self, foo: str, bar: bool) -> bool: ...
    def return_type_less_specific(self, foo: int, bar: str) -> Any: ...
    def return_type_wrong(self, foo: int, bar: str) -> str: ...
