from testing.util import MypyNodeFactory

from .compare import MatchResult, compare_symbols


class TestCompareTypevars:
    def test_plain_type_var(self, mypy_nodes: MypyNodeFactory) -> None:
        symbol, reference = mypy_nodes.get_plain_type_var()
        result = compare_symbols(symbol, reference)
        assert result.match_result is MatchResult.MATCH

    def test_bound_type_var(self, mypy_nodes: MypyNodeFactory) -> None:
        symbol, reference = mypy_nodes.get_bound_type_var()
        result = compare_symbols(symbol, reference)
        assert result.match_result is MatchResult.MATCH

    def test_bound_type_var_more_specific(self, mypy_nodes: MypyNodeFactory) -> None:
        symbol, reference = mypy_nodes.get_bound_type_var_more_specific()
        result = compare_symbols(symbol, reference)
        assert result.match_result is MatchResult.MATCH

    def test_values_type_var(self, mypy_nodes: MypyNodeFactory) -> None:
        symbol, reference = mypy_nodes.get_values_type_var()
        result = compare_symbols(symbol, reference)
        assert result.match_result is MatchResult.MATCH

    def test_values_type_var_no_values_in_generated(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        symbol, reference = mypy_nodes.get_values_type_var_no_values_in_generated()
        result = compare_symbols(symbol, reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_values_type_var_more_specific(self, mypy_nodes: MypyNodeFactory) -> None:
        symbol, reference = mypy_nodes.get_values_type_var_more_specific()
        result = compare_symbols(symbol, reference)
        assert result.match_result is MatchResult.MATCH
