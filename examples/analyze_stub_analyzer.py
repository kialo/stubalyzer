import os
from pathlib import Path

# goes through all python stubs (.pyi files) and lists their exported symbols with type annotation
from typing import Iterable, List

from stub_analyzer.api import RelevantSymbolNode, compare_types, get_stub_types

base_dir = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
mypy_conf = base_dir / "mypy.ini"

hand_written: List[RelevantSymbolNode] = list(
    get_stub_types(f"{base_dir}/stubs-handwritten", mypy_conf_path=str(mypy_conf))
)
generated: List[RelevantSymbolNode] = list(
    get_stub_types(f"{base_dir}/stubs-generated", mypy_conf_path=str(mypy_conf))
)


def _print_graph_data(stub_types: Iterable[RelevantSymbolNode]) -> None:
    for symbol in stub_types:
        type_name = str(symbol.type) if hasattr(symbol, "type") else type(symbol)
        print(f"{symbol.fullname()}: {type_name}")


# print("Hand-written Stubs:\n")
# _print_graph_data(hand_written)

gen_map = {symbol.fullname(): symbol for symbol in generated}


def resolve_generated_symbol(symbol, gen_map):
    """Resolve the given symbol in the generated stubs.
    
    Maybe move this to api.py?"""
    generated_symbol = gen_map.get(symbol.fullname())
    if generated_symbol:
        return generated_symbol

    klass = symbol.info
    if not klass:
        return None

    klass_node = gen_map.get(klass.fullname())
    if not klass_node:
        return None

    res = klass_node.get(symbol.name())
    return gen_map.get(res.fullname)


def compare(hand_written, generated):
    """Compare hand written to generated stubs."""
    gen_map = {symbol.fullname(): symbol for symbol in generated}

    for symbol in hand_written:
        if symbol.fullname().startswith("passlib"):
            generated_symbol = resolve_generated_symbol(symbol, gen_map)
            if not generated_symbol:
                print(
                    f"Could not resolve symbol {symbol.fullname()} in generated stubs."
                )
            else:
                yield compare_types(symbol, generated_symbol)


comp_res = list(compare(hand_written, generated))

for res in comp_res:
    if not res.match:
        print()
        print(res.message)
