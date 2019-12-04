import pytest
from mypy.nodes import FuncDef, Node

from . import GeneratedStubNotFound, HandwrittenStubNotFound, mypy_node_factory


class TestMypyNodeFactory:
    def test_get_returns_correct_node(self) -> None:
        requested_node_fullname = "mypy_node_factory_test_nodes.same_type_function"
        node, node_ref = mypy_node_factory.get(requested_node_fullname, FuncDef)

        assert type(node) == type(node_ref)
        assert node != node_ref
        assert node.fullname == requested_node_fullname

    def test_get_throws_handwritten_stub_not_found_error_if_handwritten_missing(
        self,
    ) -> None:
        mypy_node_fullname = "mypy_node_factory_test_nodes.not_in_handwritten"

        with pytest.raises(
            HandwrittenStubNotFound,
            match=f"Handwritten stub {mypy_node_fullname} not found",
        ):
            mypy_node_factory.get(mypy_node_fullname, Node)

    def test_get_throws_generated_stub_not_found_error_if_generated_missing(
        self,
    ) -> None:
        mypy_node_fullname = "mypy_node_factory_test_nodes.not_in_generated"

        with pytest.raises(
            GeneratedStubNotFound,
            match=f"Generated stub {mypy_node_fullname} not found",
        ):
            mypy_node_factory.get(mypy_node_fullname, Node)
