import pytest

from testing.util import MypyNodeFactory, mypy_node_factory


@pytest.fixture
def mypy_nodes() -> MypyNodeFactory:
    return mypy_node_factory
