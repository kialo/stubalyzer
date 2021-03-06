from typing import Any

from ._funcs import astuple as astuple
from ._make import attrib as attrib
from ._make import attrs as attrs

class VersionInfo:
    year: Any = ...
    minor: Any = ...
    micro: Any = ...
    releaselevel: Any = ...
    @classmethod
    def _from_version_string(cls, s: Any): ...
    def _ensure_tuple(self, other: Any): ...
    def __eq__(self, other: Any) -> Any: ...
    def __lt__(self, other: Any) -> Any: ...
