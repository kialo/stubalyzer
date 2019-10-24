import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict, List, Tuple

from stub_analyzer import RelevantSymbolNode, get_stub_types

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
OUTPUT_PATH = BASE_DIR / "stub_analyzer" / "test_data"


def collect_stub_types() -> Tuple[
    Dict[str, RelevantSymbolNode], Dict[str, RelevantSymbolNode]
]:
    mypy_conf = BASE_DIR / "mypy.ini"
    hand_written = {
        symbol.fullname(): symbol
        for symbol in get_stub_types(
            f"{BASE_DIR}/stubs-handwritten", mypy_conf_path=str(mypy_conf)
        )
    }
    generated = {
        symbol.fullname(): symbol
        for symbol in get_stub_types(
            f"{BASE_DIR}/stubs-generated", mypy_conf_path=str(mypy_conf)
        )
    }

    return hand_written, generated


def serialize(
    hand_written: Dict[str, RelevantSymbolNode],
    generated: Dict[str, RelevantSymbolNode],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Compare hand written to generated stubs."""

    hand_serialized: Dict[str, Any] = {}
    gen_serialized: Dict[str, Any] = {}
    for fullname, symbol in hand_written.items():
        print(f"Serializing {fullname}")
        generated_symbol = generated.get(fullname)
        if not generated_symbol:
            print(f"Could not resolve symbol {fullname} in generated stubs.")
        else:
            hand_serialized[fullname] = symbol.serialize()
            gen_serialized[fullname] = generated_symbol.serialize()

    return hand_serialized, gen_serialized


# TODO: Add option to serialize all symbols
def serialize_all_symbols() -> int:
    hand_written, generated = collect_stub_types()
    hand_serialized, gen_serialized = serialize(hand_written, generated)

    for name, data in hand_serialized.items():
        with open(str(OUTPUT_PATH / "symbols" / f"{name}.json"), "w+") as handle:
            json.dump(data, handle, indent=4)

    for name, data in gen_serialized.items():
        with open(
            str(OUTPUT_PATH / "reference_symbols" / f"{name}.json"), "w+"
        ) as handle:
            json.dump(data, handle, indent=4)

    return 0


def serialize_symbol(fullname: str) -> int:
    hand_written, generated = collect_stub_types()
    symbol = hand_written.get(fullname)

    if not symbol:
        print(f"Could not resolve symbol {fullname} in handwritten stubs.")
        return -1

    generated_symbol = generated.get(fullname)
    if not generated_symbol:
        # TODO: Allow ignoring this error
        print(f"Could not resolve symbol {symbol.fullname()} in generated stubs.")
        return -1

    with open(str(OUTPUT_PATH / "symbols" / f"{fullname}.json"), "w+") as handle:
        json.dump(symbol.serialize(), handle, indent=4)

    with open(
        str(OUTPUT_PATH / "reference_symbols" / f"{fullname}.json"), "w+"
    ) as handle:
        json.dump(generated_symbol.serialize(), handle, indent=4)

    return 0


def main(args: List[str]) -> int:
    parser = ArgumentParser(description="Serialize the type of a symbol")
    parser.add_argument(
        "fullname",
        type=str,
        help='Fully qualified name of the symbol, e.g. "passlib.hash.bcrypt"',
    )
    # TODO: Add options to change where the output should go

    options = parser.parse_args(args)

    return serialize_symbol(options.fullname)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
