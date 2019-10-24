import pytest  # type: ignore

from .type_data import TypeData


@pytest.fixture()  # type: ignore
def type_data() -> TypeData:
    return TypeData()
