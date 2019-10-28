from testing.util import MypyNodeFactory

from .lookup import LookupResult, lookup_symbol


class TestLookupOfMislocatedSymbol:
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

    def test_correctly_placed_symbol(self, mypy_nodes: MypyNodeFactory) -> None:
        hand, gen = mypy_nodes.get_method()
        gen_map = mypy_nodes.get_generated_stubs_map()

        result = lookup_symbol(gen_map, hand)
        assert result == LookupResult(symbol=gen, containing_class=gen.info)
