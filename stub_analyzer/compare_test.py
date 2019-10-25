from mypy.nodes import Var
from mypy.types import NoneType
from testing.util import MypyNodeFactory

from .compare import ComparisonResult, MatchResult, compare_symbols


class TestComparisonResult:
    def test_create_not_found_does_not_match(self) -> None:
        own_symbol = Var("x")
        data = {"fullname": "package.x"}
        result = ComparisonResult.create_not_found(own_symbol, data=data)
        assert result.matchResult is MatchResult.NOT_FOUND
        assert result.symbol is own_symbol
        assert result.reference is None
        assert result.message is not None
        assert result.data is data

    def test_create_mismatch(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", None)
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_mismatch(own_symbol, other_symbol, data=data)
        assert result.matchResult is MatchResult.MISMATCH
        assert result.symbol is own_symbol
        assert result.reference is other_symbol
        assert result.message is not None
        assert result.data is data

    def test_create_match(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", NoneType())
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_match(own_symbol, other_symbol, data=data)
        assert result.matchResult is MatchResult.MATCH
        assert result.symbol is own_symbol
        assert result.reference is other_symbol
        assert result.message is not None
        assert result.data is data


class TestCompareSymbols:
    def test_right_type_is_none_succeeds(self) -> None:
        own = Var("x", NoneType())  # the type of "None"
        other = Var("x", None)  # actually missing
        result = compare_symbols(own, other)
        assert result.matchResult is MatchResult.MATCH
        assert result.message == "Generated type is None"

    def test_both_types_are_none_succeeds(self) -> None:
        own = Var("x", None)
        other = Var("x", None)
        result = compare_symbols(own, other)
        assert result.matchResult is MatchResult.MATCH

    def test_left_is_none_fails(self) -> None:
        own = Var("x", None)  # actually missing
        other = Var("x", NoneType())  # the type of "None"
        result = compare_symbols(own, other)
        assert result.matchResult is MatchResult.MISMATCH

    def test_both_types_are_none_type_succeeds(self) -> None:
        own = Var("x", NoneType())
        other = Var("x", NoneType())
        result = compare_symbols(own, other)
        assert result.matchResult is MatchResult.MATCH

    def test_type_infos_with_same_name_match(self, mypy_nodes: MypyNodeFactory) -> None:
        cls, cls_reference = mypy_nodes.get_class_with_method()
        result = compare_symbols(cls, cls_reference)

        assert result.matchResult is MatchResult.MATCH

    def test_type_infos_with_different_names_mismatch(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        supercls, _ = mypy_nodes.get_class_with_method()
        sublcls, _ = mypy_nodes.get_subclass_with_method()
        result = compare_symbols(supercls, sublcls)

        assert result.matchResult is MatchResult.MISMATCH

    def test_func_def_mismatches_when_handwritten_stub_has_additional_optional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func_def, func_def_reference = mypy_nodes.get_additional_optional_args_node()
        result = compare_symbols(func_def, func_def_reference)
        assert result.matchResult is MatchResult.MISMATCH

    def test_func_def_mismatches_when_handwritten_stub_has_additional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func_def, func_def_reference = mypy_nodes.get_additional_args_node()
        result = compare_symbols(func_def, func_def_reference)
        assert result.matchResult is MatchResult.MISMATCH

    def test_overload_mismatches_if_any_handwritten_stub_has_additional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        overloaded_def, overloaded_reference = (
            mypy_nodes.get_overloaded_additional_args_node()
        )
        result = compare_symbols(overloaded_def, overloaded_reference)
        assert result.matchResult is MatchResult.MISMATCH

    def test_overload_mismatch_if_any_handwritten_stub_has_additional_optional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        overloaded_def, overloaded_reference = (
            mypy_nodes.get_overloaded_additional_optional_args_node()
        )
        result = compare_symbols(overloaded_def, overloaded_reference)
        assert result.matchResult is MatchResult.MISMATCH
