from typing import Any, Type, TypeVar

from passlib.ifc import PasswordHash

_MinimalHandlerT = TypeVar("_MinimalHandlerT", bound="MinimalHandler")
_TruncateMixinT = TypeVar("_TruncateMixinT", bound="TruncateMixin")

class MinimalHandler(PasswordHash):
    @classmethod
    def using(
        cls: Type[_MinimalHandlerT], relaxed: bool = ..., **kwds: Any
    ) -> Type[_MinimalHandlerT]: ...

class TruncateMixin(MinimalHandler):
    @classmethod
    def using(
        cls: Type[_TruncateMixinT], relaxed: bool = ..., **kwds: Any
    ) -> Type[_TruncateMixinT]: ...

class GenericHandler(MinimalHandler):
    @classmethod
    def hash(cls, secret: str) -> str: ...
    @classmethod
    def identify(cls, hash: bytes) -> str: ...
