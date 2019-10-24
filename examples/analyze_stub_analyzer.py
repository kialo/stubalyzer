import json
import os
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple

from mypy.nodes import TypeInfo
from stub_analyzer import (
    ComparisonResult,
    RelevantSymbolNode,
    compare_symbols,
    get_stub_types,
)


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


def serialize(
    hand_written: List[RelevantSymbolNode], generated: List[RelevantSymbolNode]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Compare hand written to generated stubs."""
    gen_map = {symbol.fullname(): symbol for symbol in generated}

    hand_serialized: Dict[str, Any] = {}
    gen_serialized: Dict[str, Any] = {}
    for symbol in hand_written:
        print(f"Serializing {symbol.fullname()}")
        generated_symbol = gen_map.get(symbol.fullname())
        if not generated_symbol:
            print(f"Could not resolve symbol {symbol.fullname()} in generated stubs.")
        else:
            hand_serialized[symbol.fullname()] = symbol.serialize()
            gen_serialized[generated_symbol.fullname()] = generated_symbol.serialize()

    return hand_serialized, gen_serialized


def collect_types() -> Tuple[List[RelevantSymbolNode], List[RelevantSymbolNode]]:
    base_dir = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
    mypy_conf = base_dir / "mypy.ini"

    hand_written: List[RelevantSymbolNode] = list(
        get_stub_types(f"{base_dir}/stubs-handwritten", mypy_conf_path=str(mypy_conf))
    )
    generated: List[RelevantSymbolNode] = list(
        get_stub_types(f"{base_dir}/stubs-generated", mypy_conf_path=str(mypy_conf))
    )

    return hand_written, generated


def serialize_types_main() -> None:
    hand_written, generated = collect_types()
    hand_serialized, gen_serialized = serialize(hand_written, generated)

    with open("handwritten.json", "w+") as handle:
        json.dump(hand_serialized, handle, indent=4)

    with open("generated.json", "w+") as handle:
        json.dump(gen_serialized, handle, indent=4)


def compare_main() -> None:
    hand_written, generated = collect_types()
    comp_res = list(compare(hand_written, generated))

    for res in comp_res:
        print(res.message)
        print(type(res).__name__ + "(")
        for key, val in res._asdict().items():
            print(f"    {key}={repr(val)}")
        print(")")
        print("-----------------------------")


if __name__ == "__main__":
    serialize_types_main()
