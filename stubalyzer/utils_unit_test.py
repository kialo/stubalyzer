from unittest.mock import Mock

from mypy.nodes import Expression

from .utils import get_expression_fullname


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
        self,
    ) -> None:
        fullname_mock = Mock(return_value=13245)
        expression = Mock(fullname=fullname_mock, spec=Expression)
        assert get_expression_fullname(expression) is None
