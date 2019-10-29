import asyncio
from typing import Iterable

DEFAULT_LINE_LENGTH: str

def shutdown(loop: str) -> None: ...

class NotFound:
    pass

def cancel(tasks: Iterable[asyncio.Task]) -> None: ...
