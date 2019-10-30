from typing import Any

class PasswordHash:
    @classmethod
    def encrypt(cls, *args: Any, **setting_and_context_kwds: Any) -> str: ...
