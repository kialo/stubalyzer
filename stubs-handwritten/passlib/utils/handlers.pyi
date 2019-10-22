from typing import Any

from passlib.ifc import PasswordHash

class MinimalHandler(PasswordHash):
    @classmethod
    def using(cls, relaxed: bool = ..., **kwds: Any) -> MinimalHandler: ...

class TruncateMixin(MinimalHandler):
    @classmethod
    def using(cls, relaxed: bool = ..., **kwds: Any) -> TruncateMixin: ...

class GenericHandler(MinimalHandler):
    @classmethod
    def hash(cls, secret: str) -> str: ...
    @classmethod
    def identify(cls, hash: bytes) -> str: ...
