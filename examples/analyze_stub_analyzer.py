import os
from pathlib import Path
from typing import Dict, Generator, List

from mypy.nodes import TypeInfo
from stub_analyzer import (
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
            klass_node = gen_map.get(klass.fullname())
            if not klass_node:
                continue

            if not isinstance(klass_node, TypeInfo):
                continue

            res = klass_node.get(symbol.name())
            if not (res and res.fullname):
                continue

            gen_res = gen_map.get(res.fullname)
            if gen_res:
                print("Found generated method:")
                print(repr(getattr(gen_res, "type", None)))
        else:
            yield compare_symbols(symbol, generated_symbol)


comp_res = list(compare(hand_written, generated))

for res in comp_res:
    print(res.message)
    print(type(res).__name__ + "(")
    for key, val in res._asdict().items():
        print(f"    {key}={repr(val)}")
    print(")")
    print("-----------------------------")
