import os
from pathlib import Path
from typing import Dict, Generator, Iterable, List

from mypy.nodes import TypeInfo
from stub_analyzer.api import (
    ComparisonResult,
    RelevantSymbolNode,
    compare_symbols,
    get_stub_types,
)

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

gen_map: Dict[str, RelevantSymbolNode] = {
    symbol.fullname(): symbol for symbol in generated
}


def compare(
    hand_written: List[RelevantSymbolNode], generated: List[RelevantSymbolNode]
) -> Generator[ComparisonResult, None, None]:
    """Compare hand written to generated stubs."""
    gen_map = {symbol.fullname(): symbol for symbol in generated}

    for symbol in hand_written:
        generated_symbol = gen_map.get(symbol.fullname())
        if not generated_symbol:
            print(f"Could not resolve symbol {symbol.fullname()} in generated stubs.")
            klass = getattr(symbol, "info", None)
            if not klass:
                continue
            # print(f"Found symbol on class: {klass}")
            klass_node = gen_map.get(klass.fullname())
            if not klass_node:
                continue

            # print(f"Found class in generated types: {klass_node}")
            if not isinstance(klass_node, TypeInfo):
                continue

            res = klass_node.get(symbol.name())
            if not (res and res.fullname):
                continue

            # print(f"Found method on class: {res}")
            res = gen_map.get(res.fullname)
            if res:
                print("Found generated method:")
                print(repr(res.type))
        else:
            yield compare_symbols(symbol, generated_symbol)


comp_res = list(compare(hand_written, generated))

for res in comp_res:
    if not res.match:
        print()
        print(res.message)
