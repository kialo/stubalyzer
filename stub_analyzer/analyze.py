import re
import sys
from argparse import ArgumentParser, Namespace
from typing import Generator, List

from mypy.nodes import TypeAlias, TypeVarExpr, Var

from stub_analyzer import (
    ComparisonResult,
    RelevantSymbolNode,
    compare_symbols,
    get_stub_types,
)


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        description="Analyze a set of (handcrafted) mypy stubs "
        + "by comparing them to (generated) reference stubs"
    )
    parser.add_argument("-c", "--config", required=True, help="Mypy config file")
    parser.add_argument(
        "stubs_handwritten",
        help="Directory of handwritten stubs that need to be analyzed",
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
        name = symbol.fullname()
        if name in gen_map:
            yield compare_symbols(symbol, gen_map[name])
        elif isinstance(symbol, (TypeAlias, TypeVarExpr, Var)) and re.match(
            r"_[^_].*", name.split(".")[-1]
        ):
            # Ignore symbols that begin with (exactly) one _,
            # since we assume they are private
            continue
        else:
            yield ComparisonResult.create_not_found(symbol)


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
