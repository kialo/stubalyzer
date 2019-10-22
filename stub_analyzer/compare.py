"""
Compare mypy types.
"""
from typing import Any, Dict, NamedTuple, Optional

from mypy.meet import is_overlapping_types
from mypy.nodes import CONTRAVARIANT, COVARIANT, TypeAlias, TypeInfo, TypeVarExpr
from mypy.subtypes import is_subtype
from mypy.types import Type as TypeNode

from .types import RelevantSymbolNode


class ComparisonResult(NamedTuple):
    match: bool
    symbol_a: RelevantSymbolNode
    symbol_b: Optional[RelevantSymbolNode]
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def create_not_found(
        cls,
        symbol_a: RelevantSymbolNode,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ComparisonResult":
        return cls(
            match=False,
            symbol_a=symbol_a,
            symbol_b=None,
            message=(
                message
                or (f"Symbol {symbol_a.fullname()} not found in generated stubs.")
            ),
            data=data,
        )

    @classmethod
    def create_mismatch(
        cls,
        symbol_a: RelevantSymbolNode,
        symbol_b: RelevantSymbolNode,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ComparisonResult":
        return cls(
            match=False,
            symbol_a=symbol_a,
            symbol_b=symbol_b,
            message=(
                message
                or (
                    f"Types of {symbol_a.fullname()} ({type(symbol_a)},"
                    f" {getattr(symbol_a, 'type', None)})"
                    f" and {symbol_b.fullname()} ({type(symbol_b)},"
                    f" {getattr(symbol_b, 'type', None)}) do not match."
                )
            ),
            data=data,
        )

    @classmethod
    def create_match(
        cls,
        symbol_a: RelevantSymbolNode,
        symbol_b: RelevantSymbolNode,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ComparisonResult":
        return cls(
            match=True,
            symbol_a=symbol_a,
            symbol_b=symbol_b,
            message=(
                message
                or (
                    f"Types of {symbol_a.fullname()} ({type(symbol_a)},"
                    f" {getattr(symbol_a, 'type', None)})"
                    f" and {symbol_b.fullname()} ({type(symbol_b)},"
                    f" {getattr(symbol_b, 'type', None)}) match."
                )
            ),
            data=data,
        )


def _mypy_types_match(a: TypeNode, b: TypeNode) -> bool:
    return is_overlapping_types(a, b) or is_subtype(a, b)


def _compare_mypy_types(
    a: RelevantSymbolNode,
    b: RelevantSymbolNode,
    a_type: Optional[TypeNode],
    b_type: Optional[TypeNode],
) -> ComparisonResult:
    if b_type is None:
        # Mypy does not have enought type information
        # so we accept that our stub is correct
        return ComparisonResult.create_match(
            symbol_a=a, symbol_b=b, message="Generated type is None"
        )

    if a_type is None:
        return ComparisonResult.create_mismatch(symbol_a=a, symbol_b=b)

    if _mypy_types_match(a_type, b_type):
        return ComparisonResult.create_match(
            symbol_a=a,
            symbol_b=b,
            data={
                "a_name": a.fullname(),
                "a_type": a_type,
                "b_name": b.fullname(),
                "b_type": b_type,
                "overlap": is_overlapping_types(a_type, b_type),
                "subtype": is_subtype(a_type, b_type),
            },
        )

    return ComparisonResult.create_mismatch(symbol_a=a, symbol_b=b)


def _compare_type_infos(a: TypeInfo, b: TypeInfo) -> ComparisonResult:
    """Compare TypeInfo nodes, which are class definitions.

    Currently only does a comparison on the fullname, since we only
    care that the class is defined at the same location under the same name.
    """
    if a.fullname() == b.fullname():
        return ComparisonResult.create_match(symbol_a=a, symbol_b=b)
    else:
        return ComparisonResult.create_mismatch(symbol_a=a, symbol_b=b)


def _compare_type_aliases(a: TypeAlias, b: TypeAlias) -> ComparisonResult:
    """Compare TypeAlias nodes.

    TypeAlias nodes contain the referenced type as the target.
    """
    return _compare_mypy_types(a, b, a.target, b.target)


def _format_type_var(x: TypeVarExpr) -> str:
    """Format a TypeVarExpr as it would be written in code."""
    variance = ""
    if x.variance == COVARIANT:
        variance = ", covariant=True"
    elif x.variance == CONTRAVARIANT:
        variance = ", contravariant=True"

    values = ""
    if x.values:
        values = ", " + (", ".join(str(t) for t in x.values))

    return f"{x.name} = TypeVar('{x.name}'{values}{variance})"


def _compare_type_var_expr(a: TypeVarExpr, b: TypeVarExpr) -> ComparisonResult:
    raise NotImplementedError(
        "Comparison of type variables (TypeVarExpr) is not implemented"
        f"\n{_format_type_var(a)}"
        f"\n{_format_type_var(b)}"
    )


def compare_symbols(a: RelevantSymbolNode, b: RelevantSymbolNode) -> ComparisonResult:
    """Check if symbol node a is compatible with b."""

    # TODO: Check if this is always the case, i.e. could there be
    # cases where a and b don't have the same class but still match?
    if type(a) != type(b):
        return ComparisonResult.create_mismatch(symbol_a=a, symbol_b=b)

    if isinstance(a, TypeInfo) and isinstance(b, TypeInfo):
        return _compare_type_infos(a, b)

    if isinstance(a, TypeAlias) and isinstance(b, TypeAlias):
        return _compare_type_aliases(a, b)

    if isinstance(a, TypeVarExpr) and isinstance(b, TypeVarExpr):
        return _compare_type_var_expr(a, b)

    return _compare_mypy_types(a, b, getattr(a, "type"), getattr(b, "type"))
