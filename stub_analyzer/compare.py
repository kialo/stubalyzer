"""
Compare mypy types.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, NamedTuple, Optional
from warnings import warn

from mypy.meet import is_overlapping_types
from mypy.nodes import (
    CONTRAVARIANT,
    COVARIANT,
    Argument,
    FuncDef,
    TypeAlias,
    TypeInfo,
    TypeVarExpr,
)
from mypy.subtypes import is_subtype
from mypy.types import CallableType, Overloaded
from mypy.types import Type as TypeNode

from .types import RelevantSymbolNode


class MatchResult(Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    NOT_FOUND = "not_found"

    @classmethod
    def declare_mismatch(cls, matchResultString: str) -> "MatchResult":
        if matchResultString == MatchResult.MATCH.value:
            raise ValueError(
                f"'{MatchResult.MATCH.value}' is not a valid mismatch type."
                f"(Use {', '.join([m.value for m in MatchResult])})"
            )
        return MatchResult(matchResultString)


def _get_symbol_type_info(symbol: RelevantSymbolNode) -> str:
    """
    Get the type of the given symbol as a human readable string.

    :param symbol: symbol for which to get the type
    """
    if isinstance(symbol, TypeAlias):
        return repr(symbol.target)
    if isinstance(symbol, TypeVarExpr):
        return _format_type_var(symbol)
    if isinstance(symbol, TypeInfo):
        return f"Class({symbol.fullname()})"

    return repr(symbol.type)


class ComparisonResult(NamedTuple):
    """
    Result of comparing two symbol nodes and their types.
    """

    matchResult: MatchResult
    """Type of comparison result"""

    symbol: RelevantSymbolNode
    """Symbol that was checked"""

    reference: Optional[RelevantSymbolNode]
    """Reference symbol that was checked against"""

    symbol_name: str
    """Full name of the symbol that was checked"""

    symbol_type: str
    """Type of the symbol that was checked"""

    reference_name: Optional[str]
    """Full name of the reference symbol"""

    reference_type: Optional[str]
    """Type of the reference symbol"""

    data: Optional[Dict[str, Any]] = None
    """Optional additional data"""

    message_val: Optional[str] = None
    """Optional message"""

    @property
    def message(self) -> str:
        """Human readable result of the comparison."""
        if self.message_val:
            return self.message_val

        if self.matchResult is MatchResult.MATCH:
            return "\n".join(
                [
                    f"Types for {self.symbol_name} match:",
                    f"    {self.symbol_type}",
                    f"    {self.reference_type}",
                ]
            )
        elif self.matchResult is MatchResult.MISMATCH:
            return "\n".join(
                [
                    f"Types for {self.symbol_name} do not match:",
                    f"    {self.symbol_type}",
                    f"    {self.reference_type}",
                ]
            )
        elif self.matchResult is MatchResult.NOT_FOUND:
            return f'Symbol "{self.symbol_name}" not found in generated stubs'

    @classmethod
    def _create(
        cls,
        matchResult: MatchResult,
        symbol: RelevantSymbolNode,
        reference: Optional[RelevantSymbolNode],
        data: Optional[Dict[str, Any]],
        message: Optional[str],
    ) -> ComparisonResult:
        """
        Create a comparison result.

        :param match: if the match was successful
        :param symbol: symbol that was checked
        :param reference: reference symbol that was checked against
        :param data: optional additional data
        :param message: optional message
        """
        return cls(
            matchResult=matchResult,
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
        """
        Create an unsuccessful comparison result
        where there was no reference symbol found.

        :param symbol: symbol we wanted to check
        :param data: optional additional data
        :param message: optional message
        """
        return cls._create(
            matchResult=MatchResult.NOT_FOUND,
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
        """
        Create an unsuccessful comparison result.

        :param symbol: symbol that was checked
        :param reference: reference symbol that was checked against
        :param data: optional additional data
        :param message: optional message
        """
        return cls._create(
            matchResult=MatchResult.MISMATCH,
            symbol=symbol,
            reference=reference,
            data=data,
            message=message,
        )

    @classmethod
    def create_match(
        cls,
        symbol: RelevantSymbolNode,
        reference: RelevantSymbolNode,
        data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> ComparisonResult:
        """
        Create a successful comparison result.

        :param symbol: symbol that was checked
        :param reference: reference symbol that was checked against
        :param data: optional additional data
        :param message: optional message
        """
        return cls._create(
            matchResult=MatchResult.MATCH,
            symbol=symbol,
            reference=reference,
            data=data,
            message=message,
        )


def _mypy_types_match(symbol_type: TypeNode, reference_type: TypeNode) -> bool:
    """
    Check if the given symbol type matches the the reference type.

    :param symbol_type: symbol type to check
    :param reference_type: reference type to check against
    """
    return is_overlapping_types(symbol_type, reference_type) or is_subtype(
        symbol_type, reference_type
    )


def _callable_types_match(typ: CallableType, type_reference: CallableType) -> bool:

    type_argument_list: List[Argument] = []
    type_reference_argument_list: List[Argument] = []

    if not isinstance(typ.definition, FuncDef):
        warn(f"CallableType {typ.name} does not have a definition", Warning)
    elif not isinstance(type_reference.definition, FuncDef):
        warn(f"CallableType {type_reference.name} does not have a definition", Warning)
    else:
        type_argument_list = typ.definition.arguments
        type_reference_argument_list = type_reference.definition.arguments

    return len(type_argument_list) <= len(
        type_reference_argument_list
    ) and _mypy_types_match(typ, type_reference)


def _overloaded_types_match(a: Overloaded, b: Overloaded) -> bool:
    if len(a.items()) != len(b.items()):
        return False

    return all([_callable_types_match(_a, _b) for _a, _b in zip(a.items(), b.items())])


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

    -  the reference type is None (this means mypy doesn't have enough information)
    -  the symbol type is a subtype of the reference type
    -  the symbol type overlaps with the reference type

    :param symbol: symbol node to validate
    :param reference: symbol node to validate against
    :param symbol_type: type of the symbol to validate
    :param reference_type: type of the symbol to validate against
    """
    if reference_type is None:
        # MyPy does not have enough type information
        # hence we accept that our stub is correct
        return ComparisonResult.create_match(
            symbol=symbol, reference=reference, message="Generated type is None"
        )

    if symbol_type is None:
        return ComparisonResult.create_mismatch(symbol=symbol, reference=reference)

    match = ComparisonResult.create_match(
        symbol=symbol,
        reference=reference,
        data={
            "a_name": symbol.fullname(),
            "a_type": symbol_type,
            "b_name": reference.fullname(),
            "b_type": reference_type,
            "overlap": is_overlapping_types(symbol_type, reference_type),
            "subtype": is_subtype(symbol_type, reference_type),
        },
    )

    mismatch = ComparisonResult.create_mismatch(symbol=symbol, reference=reference)

    if isinstance(symbol_type, CallableType) and isinstance(
        reference_type, CallableType
    ):
        if _callable_types_match(symbol_type, reference_type):
            return match
        return mismatch

    if isinstance(symbol_type, Overloaded) and isinstance(reference_type, Overloaded):
        if _overloaded_types_match(symbol_type, reference_type):
            return match
        return mismatch

    if _mypy_types_match(symbol_type, reference_type):
        return match

    return mismatch


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
    """
    Format a TypeVarExpr as it would be written in code.

    :param symbol: TypeVarExpr to format
    """

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
    """
    Check if a TypeVarExpr symbol matches the reference.

    Currently not implemented as we do not expect TypeVar's in stubgen stubs.

    :param symbol: type var symbol to validate
    :param reference: type var symbol to validate against
    :raises NotImplementedError: always
    """
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

    -  the symbols describe the same class

    -  the symbols are type aliases that resolve to the same type

    -  ``symbol`` is a valid subtype of ``reference``
       (see :py:func:`mypy.subtypes.is_subtype`)

    -  ``symbol`` and ``reference`` somehow overlap
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
