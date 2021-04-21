from typing import Any, Optional

from . import _config as _config
from ._compat import PY2 as PY2
from ._compat import isclass as isclass
from ._compat import iteritems as iteritems
from ._compat import metadata_proxy as metadata_proxy
from ._compat import ordered_dict as ordered_dict
from ._compat import set_closure_cell as set_closure_cell
from .exceptions import DefaultAlreadySetError as DefaultAlreadySetError
from .exceptions import FrozenInstanceError as FrozenInstanceError
from .exceptions import NotAnAttrsClassError as NotAnAttrsClassError
from .exceptions import PythonTooOldError as PythonTooOldError
from .exceptions import UnannotatedAttributeError as UnannotatedAttributeError

_obj_setattr: Any
_init_converter_pat: str
_init_factory_pat: str
_tuple_property_pat: str
_classvar_prefixes: Any
_hash_cache_field: str
_empty_metadata_singleton: Any
_sentinel: Any

class _Nothing:
    _singleton: Any = ...
    def __new__(cls): ...
    def __repr__(self): ...

NOTHING: Any

def attrib(
    default: Any = ...,
    validator: Optional[Any] = ...,
    repr: bool = ...,
    cmp: Optional[Any] = ...,
    hash: Optional[Any] = ...,
    init: bool = ...,
    metadata: Optional[Any] = ...,
    type: Optional[Any] = ...,
    converter: Optional[Any] = ...,
    factory: Optional[Any] = ...,
    kw_only: bool = ...,
    eq: Optional[Any] = ...,
    order: Optional[Any] = ...,
): ...
def _make_attr_tuple_class(cls_name: Any, attr_names: Any): ...

_Attributes: Any

def _is_class_var(annot: Any): ...
def _get_annotations(cls): ...
def _counter_getter(e: Any): ...
def _transform_attrs(cls, these: Any, auto_attribs: Any, kw_only: Any): ...
def _frozen_setattrs(self, name: Any, value: Any) -> None: ...
def _frozen_delattrs(self, name: Any) -> None: ...

class _ClassBuilder:
    __slots__: Any = ...
    _cls: Any = ...
    _cls_dict: Any = ...
    _attrs: Any = ...
    _base_names: Any = ...
    _base_attr_map: Any = ...
    _attr_names: Any = ...
    _slots: Any = ...
    _frozen: Any = ...
    _weakref_slot: Any = ...
    _cache_hash: Any = ...
    _has_post_init: Any = ...
    _delete_attribs: Any = ...
    _is_exc: Any = ...
    def __init__(
        self,
        cls: Any,
        these: Any,
        slots: Any,
        frozen: Any,
        weakref_slot: Any,
        auto_attribs: Any,
        kw_only: Any,
        cache_hash: Any,
        is_exc: Any,
    ) -> None: ...
    def __repr__(self): ...
    def build_class(self): ...
    def _patch_original_class(self): ...
    def _create_slots_class(self): ...
    def add_repr(self, ns: Any): ...
    def add_str(self): ...
    def make_unhashable(self): ...
    def add_hash(self): ...
    def add_init(self): ...
    def add_eq(self): ...
    def add_order(self): ...
    def _add_method_dunders(self, method: Any): ...

_CMP_DEPRECATION: str

def _determine_eq_order(cmp: Any, eq: Any, order: Any): ...
def attrs(
    maybe_cls: Optional[Any] = ...,
    these: Optional[Any] = ...,
    repr_ns: Optional[Any] = ...,
    repr: bool = ...,
    cmp: Optional[Any] = ...,
    hash: Optional[Any] = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    auto_attribs: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: Optional[Any] = ...,
    order: Optional[Any] = ...,
): ...

_attrs = attrs

def _has_frozen_base_class(cls): ...
def _attrs_to_tuple(obj: Any, attrs: Any): ...
def _generate_unique_filename(cls, func_name: Any): ...
def _make_hash(cls, attrs: Any, frozen: Any, cache_hash: Any): ...
def _add_hash(cls, attrs: Any): ...
def __ne__(self, other: Any) -> Any: ...
def _make_eq(cls, attrs: Any): ...
def _make_order(cls, attrs: Any): ...
def _add_eq(cls, attrs: Optional[Any] = ...): ...

_already_repring: Any

def _make_repr(attrs: Any, ns: Any): ...
def _add_repr(cls, ns: Optional[Any] = ..., attrs: Optional[Any] = ...): ...
def _make_init(
    cls,
    attrs: Any,
    post_init: Any,
    frozen: Any,
    slots: Any,
    cache_hash: Any,
    base_attr_map: Any,
    is_exc: Any,
): ...
def fields(cls): ...
def fields_dict(cls): ...
def validate(inst: Any) -> None: ...
def _is_slot_cls(cls): ...
def _is_slot_attr(a_name: Any, base_attr_map: Any): ...
def _attrs_to_init_script(
    attrs: Any,
    frozen: Any,
    slots: Any,
    post_init: Any,
    cache_hash: Any,
    base_attr_map: Any,
    is_exc: Any,
): ...

class Attribute:
    __slots__: Any = ...
    def __init__(
        self,
        name: Any,
        default: Any,
        validator: Any,
        repr: Any,
        cmp: Any,
        hash: Any,
        init: Any,
        metadata: Optional[Any] = ...,
        type: Optional[Any] = ...,
        converter: Optional[Any] = ...,
        kw_only: bool = ...,
        eq: Optional[Any] = ...,
        order: Optional[Any] = ...,
    ) -> None: ...
    def __setattr__(self, name: Any, value: Any) -> None: ...
    @classmethod
    def from_counting_attr(cls, name: Any, ca: Any, type: Optional[Any] = ...): ...
    @property
    def cmp(self): ...
    def _assoc(self, **changes: Any): ...
    def __getstate__(self): ...
    def __setstate__(self, state: Any) -> None: ...
    def _setattrs(self, name_values_pairs: Any) -> None: ...

_a: Any

class _CountingAttr:
    __slots__: Any = ...
    __attrs_attrs__: Any = ...
    cls_counter: int = ...
    counter: Any = ...
    _default: Any = ...
    _validator: Any = ...
    repr: Any = ...
    eq: Any = ...
    order: Any = ...
    hash: Any = ...
    init: Any = ...
    converter: Any = ...
    metadata: Any = ...
    type: Any = ...
    kw_only: Any = ...
    def __init__(
        self,
        default: Any,
        validator: Any,
        repr: Any,
        cmp: Any,
        hash: Any,
        init: Any,
        converter: Any,
        metadata: Any,
        type: Any,
        kw_only: Any,
        eq: Any,
        order: Any,
    ) -> None: ...
    def validator(self, meth: Any): ...
    def default(self, meth: Any): ...

class Factory:
    factory: Any = ...
    takes_self: Any = ...
    def __init__(self, factory: Any, takes_self: bool = ...) -> None: ...

def make_class(
    name: Any, attrs: Any, bases: Any = ..., **attributes_arguments: Any
): ...

class _AndValidator:
    _validators: Any = ...
    def __call__(self, inst: Any, attr: Any, value: Any) -> None: ...

def and_(*validators: Any): ...