from typing import Any

class PasswordHash:
    @classmethod
    def encrypt(cls, secret: str, **setting_and_context_kwds: Any) -> str: ...
