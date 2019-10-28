from testing.util import MypyNodeFactory

from .analyze import compare
from .compare import MatchResult


class TestCompareSymbols:
    def test_generated_is_missing_a_function(self, mypy_nodes: MypyNodeFactory) -> None:
        func_def_symbol, _ = mypy_nodes.get_missing_function_node()
        result = list(compare([func_def_symbol], []))

        assert all(map(lambda x: x.match_result is MatchResult.NOT_FOUND, result))

    def test_generated_is_missing_a_class(self, mypy_nodes: MypyNodeFactory) -> None:
        class_symbol, _ = mypy_nodes.get_missing_class()
        result = list(compare([class_symbol], []))

        assert all(map(lambda x: x.match_result is MatchResult.NOT_FOUND, result))
