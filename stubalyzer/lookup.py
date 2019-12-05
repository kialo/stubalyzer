from typing import Dict, NamedTuple, Optional

from mypy.nodes import FUNC_NO_INFO, SymbolNode, TypeInfo

from .types import RelevantSymbolNode


class LookupResult(NamedTuple):
    symbol: Optional[SymbolNode]
    """Symbol that was found"""
    containing_class: Optional[TypeInfo]
    """Class the symbol was found on"""


def get_symbol_class(symbol: SymbolNode) -> Optional[TypeInfo]:
    """
    Get the class the given symbol is defined on.

    :param symbol: Symbol to retrieve the class of
    """
    cls = getattr(symbol, "info", None)
    if cls and isinstance(cls, TypeInfo):
        return cls

    return None


def lookup_symbol(
    symbol_map: Dict[str, RelevantSymbolNode], symbol_to_lookup: SymbolNode
) -> LookupResult:
    """
    Find the given symbol in the symbol map.

    Ideally the symbol is just found under the exact same ``fullname``.
    If not and the symbol is a method, this will take the symbol's class and look it up
    in the map and then try to resolve the symbol on that class using its method
    resolution order.

    If the result of the lookup has a different ``fullname`` than the original symbol
    the given symbol is defined at a different point in the class hierarchy than
    expected.

    :param symbol_map: Dictionary for looking up symbols by their full name
    :param symbol_to_lookup: Symbol to search for
    :return: The found symbol (if any) and the class it was found on (if any)
    """
    fail = LookupResult(None, None)

    symbol = symbol_map.get(symbol_to_lookup.fullname)
    if symbol:
        return LookupResult(symbol, get_symbol_class(symbol))

    # Check if we have a class on the symbol we're looking up
    cls_to_lookup = getattr(symbol_to_lookup, "info", None)
    if not cls_to_lookup or cls_to_lookup == FUNC_NO_INFO:
        return fail

    symbol_cls = symbol_map.get(cls_to_lookup.fullname)

    if not symbol_cls or not isinstance(symbol_cls, TypeInfo):
        return fail

    found_symbol_table_node = symbol_cls.get(symbol_to_lookup.name)
    if not found_symbol_table_node or not found_symbol_table_node.node:
        return fail

    return LookupResult(
        found_symbol_table_node.node, get_symbol_class(found_symbol_table_node.node)
    )
