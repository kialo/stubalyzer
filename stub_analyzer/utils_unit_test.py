from unittest.mock import Mock

from mypy.nodes import (
    ARG_NAMED,
    ARG_NAMED_OPT,
    ARG_OPT,
    ARG_POS,
    ARG_STAR,
    ARG_STAR2,
    Expression,
)

from .utils import (
    arg_star2_count,
    arg_star_count,
    get_expression_fullname,
    strict_kind_count,
)


class TestUtils:
    def test_get_expression_fullname_when_attr_is_str(self) -> None:
        expected_fullname = "random.expression.fullname"
        expression = Mock(fullname=expected_fullname, spec=Expression)
        assert get_expression_fullname(expression) == expected_fullname

    def test_get_expression_fullname_when_attr_is_none(self) -> None:
        expression = Mock(fullname=None, spec=Expression)
        assert get_expression_fullname(expression) is None

    def test_get_expression_fullname_when_attr_is_not_str_nor_none(self) -> None:
        expression = Mock(fullname=123, spec=Expression)
        assert get_expression_fullname(expression) is None

    def test_get_expression_fullname_when_attr_does_not_exist(self) -> None:
        expression = Mock(spec=Expression)
        assert get_expression_fullname(expression) is None

    def test_get_expression_fullname_when_attr_is_function_and_return_str(self) -> None:
        expected_fullname = "random.expression.fullname.from_method"
        fullname_mock = Mock(return_value=expected_fullname)
        expression = Mock(fullname=fullname_mock, spec=Expression)
        assert get_expression_fullname(expression) is expected_fullname

    def test_get_expression_fullname_when_attr_is_function_and_do_not_return_str(
        self
    ) -> None:
        fullname_mock = Mock(return_value=13245)
        expression = Mock(fullname=fullname_mock, spec=Expression)
        assert get_expression_fullname(expression) is None

    def test_strict_kind_count(self) -> None:
        kinds = [ARG_POS, ARG_OPT, ARG_STAR, ARG_NAMED, ARG_STAR2, ARG_NAMED_OPT]
        assert strict_kind_count(kinds) == 4
        assert strict_kind_count([]) == 0
        assert strict_kind_count([ARG_STAR, ARG_STAR2]) == 0

    def test_arg_star_count(self) -> None:
        kinds = [ARG_POS, ARG_OPT, ARG_STAR, ARG_NAMED, ARG_STAR2, ARG_NAMED_OPT]
        assert arg_star_count(kinds) == 1
        assert arg_star_count([]) == 0
        assert arg_star_count([ARG_STAR, ARG_STAR]) == 2

    def test_arg_star2_count(self) -> None:
        kinds = [ARG_POS, ARG_OPT, ARG_STAR, ARG_NAMED, ARG_STAR2, ARG_NAMED_OPT]
        assert arg_star2_count(kinds) == 1
        assert arg_star2_count([]) == 0
        assert arg_star2_count([ARG_STAR2, ARG_STAR2]) == 2
