import pytest
from mypy.nodes import Var
from mypy.types import NoneType

from testing.util import MypyNodeFactory

from .compare import ComparisonResult, MatchResult, compare_symbols


def assert_match(result: ComparisonResult) -> None:
    assert result.match_result is MatchResult.MATCH


def assert_mismatch(result: ComparisonResult) -> None:
    assert result.match_result is MatchResult.MISMATCH


class TestMatchResult:
    def test_declare_mismatch(self) -> None:
        assert MatchResult.declare_mismatch("not_found") is MatchResult.NOT_FOUND
        assert MatchResult.declare_mismatch("mismatch") is MatchResult.MISMATCH
        assert (
            MatchResult.declare_mismatch("mislocated_symbol")
            is MatchResult.MISLOCATED_SYMBOL
        )
        with pytest.raises(ValueError, match=r".*not a valid mismatch type.*"):
            MatchResult.declare_mismatch("match")
        with pytest.raises(ValueError, match=r".*not a valid mismatch type.*"):
            MatchResult.declare_mismatch("blablabla")


class TestComparisonResult:
    def test_create_not_found_does_not_match(self) -> None:
        own_symbol = Var("x")
        data = {"fullname": "package.x"}
        result = ComparisonResult.create_not_found(own_symbol, data=data)
        assert result.match_result is MatchResult.NOT_FOUND
        assert result.symbol is own_symbol
        assert result.reference is None
        assert result.message is not None
        assert result.data is data

    def test_create_mismatch(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", None)
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_mismatch(own_symbol, other_symbol, data=data)
        assert result.match_result is MatchResult.MISMATCH
        assert result.symbol is own_symbol
        assert result.reference is other_symbol
        assert result.message is not None
        assert result.data is data

    def test_create_match(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", NoneType())
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_match(own_symbol, other_symbol, data=data)
        assert result.match_result is MatchResult.MATCH
        assert result.symbol is own_symbol
        assert result.reference is other_symbol
        assert result.message is not None
        assert result.data is data


class TestCompareNone:
    def test_right_type_is_none_succeeds(self) -> None:
        own = Var("x", NoneType())  # the type of "None"
        other = Var("x", None)  # actually missing
        result = compare_symbols(own, other)
        assert result.match_result is MatchResult.MATCH
        assert result.message == "Generated type is None"

    def test_both_types_are_none_succeeds(self) -> None:
        own = Var("x", None)
        other = Var("x", None)
        result = compare_symbols(own, other)
        assert result.match_result is MatchResult.MATCH

    def test_left_is_none_fails(self) -> None:
        own = Var("x", None)  # actually missing
        other = Var("x", NoneType())  # the type of "None"
        result = compare_symbols(own, other)
        assert result.match_result is MatchResult.MISMATCH

    def test_both_types_are_none_type_succeeds(self) -> None:
        own = Var("x", NoneType())
        other = Var("x", NoneType())
        result = compare_symbols(own, other)
        assert result.match_result is MatchResult.MATCH


class TestCompareTypeInfos:
    def test_type_infos_with_same_name_match(self, mypy_nodes: MypyNodeFactory) -> None:
        cls, cls_reference = mypy_nodes.get_class()
        result = compare_symbols(cls, cls_reference)

        assert result.match_result is MatchResult.MATCH

    def test_type_infos_with_different_names_mismatch(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        a_cls, _ = mypy_nodes.get_class()
        antoher_cls, _ = mypy_nodes.get_another_class()
        result = compare_symbols(a_cls, antoher_cls)

        assert result.match_result is MatchResult.MISMATCH


class TestComparePrimitiveVars:
    def test_bool_more_specific_than_int(self, mypy_nodes: MypyNodeFactory) -> None:
        int_var = mypy_nodes.get_int_var()
        bool_var = mypy_nodes.get_bool_var()

        result_a = compare_symbols(int_var, bool_var)
        result_b = compare_symbols(bool_var, int_var)

        assert result_a.match_result is MatchResult.MISMATCH
        assert result_b.match_result is MatchResult.MATCH

    def test_str_and_int_dont_match(self, mypy_nodes: MypyNodeFactory) -> None:
        int_var = mypy_nodes.get_int_var()
        str_var = mypy_nodes.get_str_var()

        result_a = compare_symbols(int_var, str_var)
        result_b = compare_symbols(str_var, int_var)

        assert result_a.match_result is MatchResult.MISMATCH
        assert result_b.match_result is MatchResult.MISMATCH


class TestCompareMethods:
    def test_compare_method(self, mypy_nodes: MypyNodeFactory) -> None:
        meth, meth_ref = mypy_nodes.get_method()
        result = compare_symbols(meth, meth_ref)
        assert result.match_result is MatchResult.MATCH

    def test_compare_classmethod(self, mypy_nodes: MypyNodeFactory) -> None:
        meth, meth_ref = mypy_nodes.get_classmethod()
        result = compare_symbols(meth, meth_ref)
        assert result.match_result is MatchResult.MATCH

    def test_compare_overridden_method(self, mypy_nodes: MypyNodeFactory) -> None:
        override, override_meth = mypy_nodes.get_overridden_method()
        result = compare_symbols(override, override_meth)
        assert result.match_result is MatchResult.MATCH

    def test_compare_overridden_classmethod(self, mypy_nodes: MypyNodeFactory) -> None:
        override, override_meth = mypy_nodes.get_overridden_classmethod()
        result = compare_symbols(override, override_meth)
        assert result.match_result is MatchResult.MATCH

    def test_argument_order_wrong(self, mypy_nodes: MypyNodeFactory) -> None:
        meth, meth_ref = mypy_nodes.get_argument_order_wrong()
        result = compare_symbols(meth, meth_ref)

        assert result.match_result is MatchResult.MISMATCH

    def test_argument_names_wrong_does_mismatch(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        meth, meth_ref = mypy_nodes.get_argument_names_wrong()
        result = compare_symbols(meth, meth_ref)
        assert result.match_result is MatchResult.MISMATCH

    def test_argument_types_wrong(self, mypy_nodes: MypyNodeFactory) -> None:
        meth, meth_ref = mypy_nodes.get_argument_types_wrong()
        result = compare_symbols(meth, meth_ref)
        assert result.match_result is MatchResult.MISMATCH

    def test_return_type_less_specific_does_match(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        meth, meth_ref = mypy_nodes.get_return_type_less_specific()
        result = compare_symbols(meth, meth_ref)
        assert result.match_result is MatchResult.MATCH

    def test_return_type_wrong(self, mypy_nodes: MypyNodeFactory) -> None:
        meth, meth_ref = mypy_nodes.get_return_type_wrong()
        result = compare_symbols(meth, meth_ref)
        assert result.match_result is MatchResult.MISMATCH


class TestCompareFunctions:
    def test_matching_functions(self, mypy_nodes: MypyNodeFactory) -> None:
        func_def, func_ref = mypy_nodes.get_matching_func_node()
        result = compare_symbols(func_def, func_ref)
        assert_match(result)

    def test_func_def_mismatches_when_handwritten_stub_has_additional_optional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func_def, func_def_reference = mypy_nodes.get_additional_optional_args_node()
        result = compare_symbols(func_def, func_def_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_func_def_mismatches_when_handwritten_stub_has_additional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func_def, func_def_reference = mypy_nodes.get_additional_args_node()
        result = compare_symbols(func_def, func_def_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_matching_with_arg_star(self, mypy_nodes: MypyNodeFactory) -> None:
        func, func_ref = mypy_nodes.get_matching_with_arg_star()
        result = compare_symbols(func, func_ref)
        assert_match(result)

    def test_matching_with_missing_arg_star(self, mypy_nodes: MypyNodeFactory) -> None:
        func, func_ref = mypy_nodes.get_matching_with_missing_arg_star()
        result = compare_symbols(func, func_ref)
        assert_mismatch(result)

    def test_mismatching_with_arg_star(self, mypy_nodes: MypyNodeFactory) -> None:
        func, func_ref = mypy_nodes.get_mismatching_with_arg_star()
        result = compare_symbols(func, func_ref)
        assert_mismatch(result)

    def test_mismatching_with_additional_arg_star(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func, func_ref = mypy_nodes.get_mismatching_with_additional_arg_star()
        result = compare_symbols(func, func_ref)
        assert_mismatch(result)

    def test_matching_with_kwarg_star2(self, mypy_nodes: MypyNodeFactory) -> None:
        func, func_ref = mypy_nodes.get_matching_with_kwarg_star2()
        result = compare_symbols(func, func_ref)
        assert_match(result)

    def test_matching_with_missing_kwarg_star2(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func, func_ref = mypy_nodes.get_matching_with_missing_kwarg_star2()
        result = compare_symbols(func, func_ref)
        assert_mismatch(result)

    def test_mismatching_with_kwarg_star2(self, mypy_nodes: MypyNodeFactory) -> None:
        func, func_ref = mypy_nodes.get_mismatching_with_kwarg_star2()
        result = compare_symbols(func, func_ref)
        assert_mismatch(result)

    def test_mismatching_with_additional_kwarg_star2(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func, func_ref = mypy_nodes.get_mismatching_with_additional_kwarg_star2()
        result = compare_symbols(func, func_ref)
        assert_mismatch(result)

    def test_overload_mismatches_if_any_handwritten_stub_has_additional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        (
            overloaded_def,
            overloaded_reference,
        ) = mypy_nodes.get_overloaded_additional_args_node()
        result = compare_symbols(overloaded_def, overloaded_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_overload_mismatch_if_any_handwritten_stub_has_additional_optional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        (
            overloaded_def,
            overloaded_reference,
        ) = mypy_nodes.get_overloaded_additional_optional_args_node()
        result = compare_symbols(overloaded_def, overloaded_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_decorated_function_matches(self, mypy_nodes: MypyNodeFactory) -> None:
        decorated, decorated_reference = mypy_nodes.get_decorated_function()
        result = compare_symbols(decorated, decorated_reference)
        assert result.match_result is MatchResult.MATCH

    def test_decorated_function_mismatches_when_handwritten_stub_has_additional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        decorated, decorated_reference = mypy_nodes.get_decorated_with_additional_args()
        result = compare_symbols(decorated, decorated_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_decorated_mismatches_if_handwritten_stub_has_additional_optional_args(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        (
            decorated,
            decorated_reference,
        ) = mypy_nodes.get_decorated_with_additional_optional_args()
        result = compare_symbols(decorated, decorated_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_generated_has_no_parameters_and_return_type(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        (
            func_def,
            func_def_reference,
        ) = mypy_nodes.get_no_parameters_and_return_type_node()
        result = compare_symbols(func_def, func_def_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_generated_has_no_parameters(self, mypy_nodes: MypyNodeFactory) -> None:
        func_def, func_def_reference = mypy_nodes.get_mismatch_with_zero_parameters()
        result = compare_symbols(func_def, func_def_reference)
        assert result.match_result is MatchResult.MISMATCH

    def test_no_annotation_matches_if_argc_matches(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        func_def, func_def_reference = mypy_nodes.get_function_with_no_annotation()
        result = compare_symbols(func_def, func_def_reference)
        assert result.match_result is MatchResult.MATCH

    def test_args_with_no_annotation_matches_if_argc_matches(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        (
            func_def,
            func_def_reference,
        ) = mypy_nodes.get_function_with_args_but_no_annotation()
        result = compare_symbols(func_def, func_def_reference)
        assert result.match_result is MatchResult.MATCH
