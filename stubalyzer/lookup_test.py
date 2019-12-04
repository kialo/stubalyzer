from copy import copy

from mypy.nodes import FUNC_NO_INFO

from testing.util import MypyNodeFactory

from .lookup import LookupResult, lookup_symbol


class TestLookupOfMislocatedSymbols:
    def test_mislocated_symbol(self, mypy_nodes: MypyNodeFactory) -> None:
        mislocated_handwritten = mypy_nodes.get_mislocated_method_handwritten()
        gen_map = mypy_nodes.get_generated_stubs_map()
        mislocated_actual_location = (
            mypy_nodes.get_mislocated_method_actual_location_generated()
        )

        result = lookup_symbol(gen_map, mislocated_handwritten)
        assert result == LookupResult(
            symbol=mislocated_actual_location,
            containing_class=mislocated_actual_location.info,
        )

    def test_mislocated_symbol_without_cls(self, mypy_nodes: MypyNodeFactory) -> None:
        mislocated_handwritten = mypy_nodes.get_mislocated_method_handwritten()
        gen_map = mypy_nodes.get_generated_stubs_map()

        original_func_info = mislocated_handwritten.info
        mislocated_handwritten.info = FUNC_NO_INFO

        result = lookup_symbol(gen_map, mislocated_handwritten)
        assert result == LookupResult(symbol=None, containing_class=None)

        mislocated_handwritten.info = original_func_info

    def test_mislocated_symbol_with_cls_not_found(
        self, mypy_nodes: MypyNodeFactory
    ) -> None:
        mislocated_handwritten = mypy_nodes.get_mislocated_method_handwritten()
        gen_map = copy(mypy_nodes.get_generated_stubs_map())

        del gen_map[mislocated_handwritten.info.fullname]
        result = lookup_symbol(gen_map, mislocated_handwritten)
        assert result == LookupResult(symbol=None, containing_class=None)

    def test_correctly_placed_symbol(self, mypy_nodes: MypyNodeFactory) -> None:
        hand, gen = mypy_nodes.get_method()
        gen_map = mypy_nodes.get_generated_stubs_map()

        result = lookup_symbol(gen_map, hand)
        assert result == LookupResult(symbol=gen, containing_class=gen.info)
