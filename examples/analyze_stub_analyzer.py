import os
from pathlib import Path

# goes through all python stubs (.pyi files) and lists their exported symbols with type annotation
from stub_analyzer.api import get_stub_types, _print_graph_data

base_dir = Path(os.path.dirname(os.path.abspath(__file__))) / '..'
mypy_conf = base_dir / "mypy.ini"
hand_written = get_stub_types(
    f"{base_dir}/stubs-handwritten", mypy_conf_path=str(mypy_conf)
)
generated = get_stub_types(f"{base_dir}/stubs-generated", mypy_conf_path=str(mypy_conf))

print("Hand-written Stubs:\n")
_print_graph_data(hand_written)

print("\n\n------------------------------------\n\n")

print("Generated stubs:\n")
_print_graph_data(generated)
