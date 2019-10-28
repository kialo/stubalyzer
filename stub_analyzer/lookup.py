from typing import Dict, NamedTuple, Optional

from mypy.nodes import SymbolNode, TypeInfo

from .types import RelevantSymbolNode


class LookupResult(NamedTuple):
    symbol: Optional[SymbolNode]
    containing_class: Optional[TypeInfo]
    """Class the symbol was found on"""


def get_symbol_class(symbol: SymbolNode) -> Optional[TypeInfo]:
    cls = getattr(symbol, "info", None)
    if cls and isinstance(cls, TypeInfo):
        return cls

    return None


def lookup_symbol(
    symbol_map: Dict[str, RelevantSymbolNode], symbol_to_lookup: SymbolNode
) -> LookupResult:
    fail = LookupResult(None, None)

    symbol = symbol_map.get(symbol_to_lookup.fullname())
    if symbol:
        return LookupResult(symbol, get_symbol_class(symbol))

    # Check if we have a class on the symbol we're looking up
    cls_to_lookup = getattr(symbol_to_lookup, "info", None)
    if not cls_to_lookup:
        return fail

    symbol_cls = symbol_map.get(cls_to_lookup.fullname())

    if not symbol_cls or not isinstance(symbol_cls, TypeInfo):
        return fail

    found_symbol_table_node = symbol_cls.get(symbol_to_lookup.name())
    if not found_symbol_table_node or not found_symbol_table_node.node:
        return fail

    return LookupResult(
        found_symbol_table_node.node, get_symbol_class(found_symbol_table_node.node)
    )
