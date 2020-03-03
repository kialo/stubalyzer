from typing import Any, Optional

from ._make import NOTHING as NOTHING
from ._make import Factory as Factory

def optional(converter: Any): ...
def default_if_none(default: Any = ..., factory: Optional[Any] = ...): ...
