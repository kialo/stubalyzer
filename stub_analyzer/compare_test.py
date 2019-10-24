from mypy.nodes import Var
from mypy.types import NoneType

from .compare import ComparisonResult, compare_symbols
from .type_data import TypeData


class TestComparisonResult:
    def test_create_not_found_does_not_match(self) -> None:
        own_symbol = Var("x")
        data = {"fullname": "package.x"}
        result = ComparisonResult.create_not_found(own_symbol, data=data)
        assert result.match is False
        assert result.symbol is own_symbol
        assert result.reference is None
        assert result.message is not None
        assert result.data is data

    def test_create_mismatch(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", None)
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_mismatch(own_symbol, other_symbol, data=data)
        assert result.match is False
        assert result.symbol is own_symbol
        assert result.reference is other_symbol
        assert result.message is not None
        assert result.data is data

    def test_create_match(self) -> None:
        own_symbol = Var("x", NoneType())
        other_symbol = Var("x", NoneType())
        data = {"name_a": "package.x", "name_b": "package.x"}
        result = ComparisonResult.create_match(own_symbol, other_symbol, data=data)
        assert result.match is True
        assert result.symbol is own_symbol
        assert result.reference is other_symbol
        assert result.message is not None
        assert result.data is data


class TestCompareSymbols:
    def test_right_type_is_none_succeeds(self) -> None:
        own = Var("x", NoneType())  # the type of "None"
        other = Var("x", None)  # actually missing
        result = compare_symbols(own, other)
        assert result.match is True
        assert result.message == "Generated type is None"

    def test_both_types_are_none_succeeds(self) -> None:
        own = Var("x", None)
        other = Var("x", None)
        result = compare_symbols(own, other)
        assert result.match is True

    def test_left_is_none_fails(self) -> None:
        own = Var("x", None)  # actually missing
        other = Var("x", NoneType())  # the type of "None"
        result = compare_symbols(own, other)
        assert result.match is False

    def test_both_types_are_none_type_succeeds(self) -> None:
        own = Var("x", NoneType())
        other = Var("x", NoneType())
        result = compare_symbols(own, other)
        assert result.match is True

    def test_type_infos_with_same_name_match(self, type_data: TypeData) -> None:
        bcrypt_symbol, bcrypt_reference = type_data.get_symbol_and_reference(
            "passlib.hash.bcrypt"
        )
        result = compare_symbols(bcrypt_symbol, bcrypt_reference)

        assert result.match is True

    def test_type_infos_with_different_names_mismatch(
        self, type_data: TypeData
    ) -> None:
        bcrypt_symbol = type_data.get_symbol("passlib.hash.bcrypt")
        md5_reference = type_data.get_reference_symbol("passlib.hash.md5_crypt")
        result = compare_symbols(bcrypt_symbol, md5_reference)

        assert result.match is False
