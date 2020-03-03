from typing import Any, Optional

from ._compat import iteritems as iteritems
from ._make import NOTHING as NOTHING
from ._make import _obj_setattr as _obj_setattr
from ._make import fields as fields
from .exceptions import AttrsAttributeNotFoundError as AttrsAttributeNotFoundError

def asdict(
    inst: Any,
    recurse: bool = ...,
    filter: Optional[Any] = ...,
    dict_factory: Any = ...,
    retain_collection_types: bool = ...,
): ...
def _asdict_anything(
    val: Any, filter: Any, dict_factory: Any, retain_collection_types: Any
): ...
def astuple(
    inst: Any,
    recurse: bool = ...,
    filter: Optional[Any] = ...,
    tuple_factory: Any = ...,
    retain_collection_types: bool = ...,
): ...
def has(cls): ...
def assoc(inst: Any, **changes: Any): ...
def evolve(inst: Any, **changes: Any): ...
