import os
from pathlib import Path

# goes through all python stubs (.pyi files) and lists their exported symbols with type annotation
from typing import Iterable, List

from stub_analyzer.api import RelevantSymbolNode, get_stub_types

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


print("Hand-written Stubs:\n")
_print_graph_data(hand_written)

print("\n\n------------------------------------\n\n")

print("Generated stubs:\n")
_print_graph_data(generated)
