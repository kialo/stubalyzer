import os
from pathlib import Path
from typing import Dict, Generator, Iterable, Tuple, cast

from mypy.nodes import SymbolNode
from stub_analyzer import (
    ComparisonResult,
    MatchResult,
    RelevantSymbolNode,
    compare_symbols,
    get_stub_types,
    lookup_symbol,
)

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".."


def collect_stub_types() -> Tuple[
    Iterable[RelevantSymbolNode], Iterable[RelevantSymbolNode]
]:
    mypy_conf = BASE_DIR / "mypy.ini"

    hand_written: Iterable[RelevantSymbolNode] = list(
        get_stub_types(f"{BASE_DIR}/stubs-handwritten", mypy_conf_path=str(mypy_conf))
    )
    generated: Iterable[RelevantSymbolNode] = list(
        get_stub_types(f"{BASE_DIR}/stubs-generated", mypy_conf_path=str(mypy_conf))
    )

    return hand_written, generated


def compare() -> Generator[ComparisonResult, None, None]:
    """Compare hand written to generated stubs."""
    hand_written, generated = collect_stub_types()
    gen_map: Dict[str, SymbolNode] = {symbol.fullname(): symbol for symbol in generated}

    for symbol in hand_written:
        gen_lookup = lookup_symbol(gen_map, symbol)
        generated_symbol = gen_lookup.symbol
        if not generated_symbol:
            print(f"Could not resolve symbol {symbol.fullname()} in generated stubs.")
        else:
            if generated_symbol.fullname() != symbol.fullname():
                print(
                    f"Found symbol {symbol.fullname()} in different location"
                    f" {generated_symbol.fullname()}"
                )
            yield compare_symbols(symbol, cast(RelevantSymbolNode, generated_symbol))


def compare_main() -> None:
    comp_res = compare()

    for res in comp_res:
        if res.matchResult is not MatchResult.MATCH:
            print(res.message)
        # print(type(res).__name__ + "(")
        # for key, val in res._asdict().items():
        #     print(f"    {key}={repr(val)}")
        # print(")")
        # print("-----------------------------")


if __name__ == "__main__":
    compare_main()