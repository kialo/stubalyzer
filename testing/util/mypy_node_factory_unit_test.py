from mypy.nodes import FuncDef, Node

from testing.util import (
    GeneratedStubNotFound,
    HandwrittenStubNotFound,
    mypy_node_factory,
)


class TestMypyNodeFactory:
    def test_get_returns_correct_node(self) -> None:
        requested_node_fullname = "mypy_node_factory_test_nodes.same_type_function"
        node, node_ref = mypy_node_factory.get(requested_node_fullname, FuncDef)

        assert type(node) == type(node_ref)
        assert node != node_ref
        assert node.fullname() == requested_node_fullname

    def test_get_throws_handwritten_stub_not_found_error_if_handwritten_missing(
        self
    ) -> None:
        error = None
        mypy_node_fullname = "mypy_node_factory_test_nodes.not_in_handwritten"
        try:
            mypy_node_factory.get(mypy_node_fullname, Node)
        except HandwrittenStubNotFound as err:
            error = err
        finally:
            assert error is not None
            assert f"Handwritten stub {mypy_node_fullname} not found" in str(error)

    def test_get_throws_generated_stub_not_found_error_if_generated_missing(
        self
    ) -> None:
        error = None

        mypy_node_fullname = "mypy_node_factory_test_nodes.not_in_generated"
        try:
            mypy_node_factory.get(mypy_node_fullname, Node)
        except GeneratedStubNotFound as err:
            error = err
        finally:
            assert error is not None
            assert f"Generated stub {mypy_node_fullname} not found" in str(error)
