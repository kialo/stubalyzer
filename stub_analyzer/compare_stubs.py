import sys
from argparse import ArgumentParser, Namespace
from typing import Generator, List

from mypy.nodes import TypeAlias, TypeVarExpr, Var

from api import (
    ComparisonResult,
    RelevantSymbolNode,
    compare_types,
    get_stub_types,
    resolve_generated_symbol,
)


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        description="Compare a handwritten mypy stubs against a reference stubs"
    )
    parser.add_argument("-c", "--config", required=True, help="Mypy config file")
    parser.add_argument(
        "stubs_handwritten",
        help="Directory of handwritten stubs that need to be checked",
    )
    parser.add_argument(
        "stubs_reference", help="Directory of reference stubs to compare against"
    )
    return parser.parse_args()


def compare(
    hand_written: List[RelevantSymbolNode], generated: List[RelevantSymbolNode]
) -> Generator[ComparisonResult, None, None]:
    """Compare hand written to generated stubs."""
    gen_map = {symbol.fullname(): symbol for symbol in generated}

    for symbol in hand_written:
        generated_symbol = resolve_generated_symbol(symbol, gen_map)
        if not generated_symbol:
            if isinstance(symbol, (TypeAlias, TypeVarExpr, Var)):
                continue
            print(f"Could not resolve symbol {symbol.fullname()} in generated stubs.")
        else:
            yield compare_types(symbol, generated_symbol)


def main() -> None:
    args = parse_command_line()
    stub_types_base = get_stub_types(
        args.stubs_handwritten, mypy_conf_path=str(args.config)
    )
    stub_types_reference = get_stub_types(
        args.stubs_reference, mypy_conf_path=str(args.config)
    )

    err = 0
    for res in compare(stub_types_base, stub_types_reference):
        if not res.match:
            err = 1
            print()
            print(res.message)

    sys.exit(err)


if __name__ == "__main__":
    main()
