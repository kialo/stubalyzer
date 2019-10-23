"""
Compare mypy types.
"""

from __future__ import annotations

from typing import Any, Dict, NamedTuple, Optional

from mypy.meet import is_overlapping_types
from mypy.nodes import CONTRAVARIANT, COVARIANT, TypeAlias, TypeInfo, TypeVarExpr
from mypy.subtypes import is_subtype
from mypy.types import Type as TypeNode

from .types import RelevantSymbolNode


def _get_symbol_type_info(symbol: RelevantSymbolNode) -> str:
    if isinstance(symbol, TypeAlias):
        return repr(symbol.target)
    if isinstance(symbol, TypeVarExpr):
        return _format_type_var(symbol)
    if isinstance(symbol, TypeInfo):
        return f"Class({symbol.fullname()})"

    return repr(symbol.type)


class ComparisonResult(NamedTuple):
    match: bool
    symbol: RelevantSymbolNode
    reference: Optional[RelevantSymbolNode]
    symbol_name: str
    symbol_type: str
    reference_name: Optional[str]
    reference_type: Optional[str]
    data: Optional[Dict[str, Any]] = None
    message_val: Optional[str] = None

    @property
    def message(self) -> str:
        if self.message_val:
            return self.message_val

        if self.match:
            return "\n".join(
                [
                    f"Types for {self.symbol_name} match:",
                    f"    {self.symbol_type}",
                    f"    {self.reference_type}",
                ]
            )

        return "\n".join(
            [
                f"Types for {self.symbol_name} do not match:",
                f"    {self.symbol_type}",
                f"    {self.reference_type}",
            ]
        )

    @classmethod
    def _create(
        cls,
        match: bool,
        symbol: RelevantSymbolNode,
        reference: Optional[RelevantSymbolNode],
        data: Optional[Dict[str, Any]],
        message: Optional[str],
    ) -> ComparisonResult:
        return cls(
            match=match,
            symbol=symbol,
            reference=reference,
            data=data,
            message_val=message,
            symbol_name=symbol.fullname(),
            symbol_type=_get_symbol_type_info(symbol),
            reference_name=reference.fullname() if reference else None,
            reference_type=_get_symbol_type_info(reference) if reference else None,
        )

    @classmethod
    def create_not_found(
        cls,
        symbol: RelevantSymbolNode,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> ComparisonResult:
        return cls._create(
            match=False,
            symbol=symbol,
            reference=None,
            data=data,
            message=(
                message or (f"Symbol {symbol.fullname()} not found in generated stubs.")
            ),
        )

    @classmethod
    def create_mismatch(
        cls,
        symbol: RelevantSymbolNode,
        reference: RelevantSymbolNode,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> ComparisonResult:
        return cls._create(
            match=False, symbol=symbol, reference=reference, data=data, message=message
        )

    @classmethod
    def create_match(
        cls,
        symbol: RelevantSymbolNode,
        reference: RelevantSymbolNode,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> ComparisonResult:
        return cls._create(
            match=True, symbol=symbol, reference=reference, data=data, message=message
        )


def _mypy_types_match(symbol: TypeNode, reference: TypeNode) -> bool:
    return is_overlapping_types(symbol, reference) or is_subtype(symbol, reference)


def compare_mypy_types(
    symbol: RelevantSymbolNode,
    reference: RelevantSymbolNode,
    symbol_type: Optional[TypeNode],
    reference_type: Optional[TypeNode],
) -> ComparisonResult:
    """
    Check if the mypy type of given symbol node is compatible with the reference
    symbol.

    Returns a successful comparison if:

    - the reference type is none (this means mypy doesn't have enough information)
    - the symbol type is a subtype of the reference type
    - the symbol type overlaps with the reference type
    """
    if reference_type is None:
        # Mypy does not have enought type information
        # so we accept that our stub is correct
        return ComparisonResult.create_match(
            symbol=symbol, reference=reference, message="Generated type is None"
        )

    if symbol_type is None:
        return ComparisonResult.create_mismatch(symbol=symbol, reference=reference)

    if _mypy_types_match(symbol_type, reference_type):
        return ComparisonResult.create_match(
            symbol=symbol,
            reference=reference,
            data={
                "overlap": is_overlapping_types(symbol_type, reference_type),
                "subtype": is_subtype(symbol_type, reference_type),
            },
        )

    return ComparisonResult.create_mismatch(symbol=symbol, reference=reference)


def _type_infos_are_same_class(
    symbol: TypeInfo, reference: TypeInfo
) -> ComparisonResult:
    """
    Check if two TypeInfo symbols are the same class.

    This currently only does a comparison of the full name,
    since we only care if the classes are defined at the same location.
    The instance fields and methods are usually checked individually already.

    :param symbol: type info symbol to validate
    :param reference: type info symbol to validate against
    """
    if symbol.fullname() == reference.fullname():
        return ComparisonResult.create_match(symbol=symbol, reference=reference)
    else:
        return ComparisonResult.create_mismatch(symbol=symbol, reference=reference)


def _compare_type_aliases(symbol: TypeAlias, reference: TypeAlias) -> ComparisonResult:
    """
    Check if a TypeAlias symbol is a valid subtype of the given reference.

    This is done by comparing the target types of the aliases.

    :param symbol: type alias symbol to validate
    :param reference: type alias symbol to validate against
    """
    return compare_mypy_types(symbol, reference, symbol.target, reference.target)


def _format_type_var(symbol: TypeVarExpr) -> str:
    """Format a TypeVarExpr as it would be written in code."""

    variance = ""
    if symbol.variance == COVARIANT:
        variance = ", covariant=True"
    elif symbol.variance == CONTRAVARIANT:
        variance = ", contravariant=True"

    values = ""
    if symbol.values:
        values = ", " + (", ".join(str(t) for t in symbol.values))

    return f"{symbol.name} = TypeVar('{symbol.name}'{values}{variance})"


def _compare_type_var_expr(
    symbol: TypeVarExpr, reference: TypeVarExpr
) -> ComparisonResult:
    raise NotImplementedError(
        "Comparison of type variables (TypeVarExpr) is not implemented, encountered:"
        f"\n - {_format_type_var(symbol)}"
        f"\n - {_format_type_var(reference)}"
    )


def compare_symbols(
    symbol: RelevantSymbolNode, reference: RelevantSymbolNode
) -> ComparisonResult:
    """
    Check if the given symbol node is compatible with the reference symbol.

    Will return a successful comparison if any of the following holds:

    - the symbols describe the same class

    - the symbols are type aliases that resolve to the same type

    - ``symbol`` is a valid subtype of ``reference``
        (see :py:func:`mypy.subtypes.is_subtype`)

    - ``symbol`` and ``reference`` somehow overlap
        (see :py:func:`mypy.meet.is_overlapping_types`)

    :param symbol: symbol node to validate
    :param reference: symbol node to validate against
    """

    # TODO: Check if this is always the case, i.e. could there be
    # cases where `symbol` and `reference` don't have the same class but still match?
    if type(symbol) != type(reference):
        return ComparisonResult.create_mismatch(symbol=symbol, reference=reference)

    if isinstance(symbol, TypeInfo) and isinstance(reference, TypeInfo):
        return _type_infos_are_same_class(symbol, reference)

    if isinstance(symbol, TypeAlias) and isinstance(reference, TypeAlias):
        return _compare_type_aliases(symbol, reference)

    if isinstance(symbol, TypeVarExpr) and isinstance(reference, TypeVarExpr):
        return _compare_type_var_expr(symbol, reference)

    return compare_mypy_types(
        symbol, reference, getattr(symbol, "type"), getattr(reference, "type")
    )
