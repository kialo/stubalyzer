import pytest  # type: ignore

from testing.util import MypyNodeFactory, mypy_node_factory

from .type_data import TypeData


@pytest.fixture()  # type: ignore
def type_data() -> TypeData:
    return TypeData()


@pytest.fixture()  # type: ignore
def mypy_nodes() -> MypyNodeFactory:
    return mypy_node_factory
