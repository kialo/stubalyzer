import pytest
from mypy.nodes import TypeVarExpr

from testing.util import MypyNodeFactory

from .compare import MatchResult, compare_symbols


class TestCompareTypevars:
    @pytest.mark.parametrize(  # type: ignore
        "node_name, expected_result",
        [
            ("typevars.PlainTypeVar", MatchResult.MATCH),
            ("typevars.BoundTypeVar", MatchResult.MATCH),
            ("typevars.BoundTypeVarMoreSpecific", MatchResult.MATCH),
            ("typevars.ValuesTypeVar", MatchResult.MATCH),
            ("typevars.ValuesTypeVarWrongOrder", MatchResult.MISMATCH),
            ("typevars.ValuesTypeVarNoValuesInGenerated", MatchResult.MISMATCH),
            ("typevars.ValuesTypeVarMoreSpecific", MatchResult.MATCH),
        ],
    )
    def test_compare_typevars(
        self, node_name: str, expected_result: MatchResult, mypy_nodes: MypyNodeFactory
    ) -> None:
        symbol, reference = mypy_nodes.get(node_name, TypeVarExpr)
        result = compare_symbols(symbol, reference)
        assert result.match_result is expected_result
