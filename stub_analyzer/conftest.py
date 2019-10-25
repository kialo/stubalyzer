import pytest  # type: ignore

from testing.util import MypyNodeFactory, mypy_node_factory


@pytest.fixture()  # type: ignore
def mypy_nodes() -> MypyNodeFactory:
    return mypy_node_factory
