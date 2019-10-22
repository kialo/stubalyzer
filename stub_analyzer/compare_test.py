from mypy.nodes import Var
from mypy.types import NoneType

from .compare import ComparisonResult


class TestComparisonResult:
    def test_create_not_found_does_not_match(self) -> None:
        own_symbol = Var("x")
        data = {"fullname": "package.x"}
        result = ComparisonResult.create_not_found(own_symbol, data=data)
        assert result.match is False
        assert result.symbol_a is own_symbol
        assert result.symbol_b is None
        assert result.message is not None
        assert result.data is data

    def test_create_mismatch(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", None)
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_mismatch(own_symbol, other_symbol, data=data)
        assert result.match is False
        assert result.symbol_a is own_symbol
        assert result.symbol_b is other_symbol
        assert result.message is not None
        assert result.data is data

    def test_create_match(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", NoneType())
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_match(own_symbol, other_symbol, data=data)
        assert result.match is True
        assert result.symbol_a is own_symbol
        assert result.symbol_b is other_symbol
        assert result.message is not None
        assert result.data is data


class TestCompareMypyTypes:
    def test_right_type_is_none(self) -> None:
        pass
