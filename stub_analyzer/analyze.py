import re
import sys
from argparse import ArgumentParser, Namespace
from json import loads as json_loads
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict, Generator, List, Set, Tuple

from mypy.nodes import TypeAlias, TypeVarExpr, Var
from schema import Schema, SchemaError, Use
from stub_analyzer import (
    ComparisonResult,
    RelevantSymbolNode,
    compare_symbols,
    get_stub_types,
)

from .compare import MatchResult

EXPECTED_MISMATCH_SCHEMA = Schema({str: Use(MatchResult.declare_mismatch)})
CHECK_FILE_ERROR = 'Check "{file_path}" to fix.'
MATCH_FOUND_ERROR = 'Expected "{symbol}" to be "{mismatch_type}" but it matched.'
WRONG_MISMATCH_ERROR = 'Expected "{symbol}" to be "{expected}" but it was "{received}".'
UNUSED_DEFINITION_ERROR = 'Expected "{symbols}" to fail, but it was not even processed.'
FILE_NOT_FOUND_WARNING = (
    'WARNING: Provided file for expected mismatches ("{file_path}") not found.'
)
SUMMARY_MESSAGE = "Comparing failed on {failed} of {total} stubs."


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        description="Analyze a set of (handcrafted) mypy stubs "
        + "by comparing them to (generated) reference stubs"
    )
    parser.add_argument("-c", "--config", required=True, help="Mypy config file")
    parser.add_argument(
        "-e",
        "--expected-mismatches",
        required=False,
        default=None,
        help="A JSON file of expected mismatching symbols and their match results",
    )
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


def setup_expected_mismatches(file_path: str) -> Tuple[Dict[str, MatchResult], str]:
    if not file_path:
        return dict(), set()

    mismatches: Dict[str, MatchResult] = {}
    mismatches_file = Path(file_path)
    if not mismatches_file.exists():
        print(FILE_NOT_FOUND_WARNING.format(file_path=file_path))
        return dict(), set()
    mismatches = EXPECTED_MISMATCH_SCHEMA.validate(
        json_loads(mismatches_file.read_text())
    )
    unused_mismatches = set(mismatches.keys())
    return mismatches, unused_mismatches


def evaluate_compare_result(
    compare_result: ComparisonResult,
    mismatches: Dict[str, MatchResult],
    mismatches_left: Set[str],
) -> int:
    symbol = compare_result.symbol_name
    matchResult = compare_result.matchResult
    err = 0
    expected_mismatch = mismatches.get(symbol)

    if expected_mismatch is None:
        if matchResult is not MatchResult.MATCH:
            err = 1
            print(f"\n{compare_result.message}")
    else:
        mismatches_left.remove(symbol)
        if matchResult is MatchResult.MATCH:
            err = 1
            print(
                "\n",
                MATCH_FOUND_ERROR.format(
                    symbol=symbol, mismatch_type=mismatches[symbol].value
                ),
            )
        elif matchResult is not expected_mismatch:
            err = 1
            print(
                "\n",
                WRONG_MISMATCH_ERROR.format(
                    symbol=symbol,
                    expected=expected_mismatch.value,
                    received=matchResult.value,
                ),
            )
    return err


def main() -> None:
    err = 0
    failed_count = 0
    total_count = 0
    args = parse_command_line()
    stub_types_base = get_stub_types(
        args.stubs_handwritten, mypy_conf_path=str(args.config)
    )
    stub_types_reference = get_stub_types(
        args.stubs_reference, mypy_conf_path=str(args.config)
    )
    try:
        mismatches, unused_mismatches = setup_expected_mismatches(
            args.expected_mismatches
        )
    except (JSONDecodeError, SchemaError) as ex:
        print(ex, "\n", CHECK_FILE_ERROR.format(file_path=args.expected_mismatches))
        err = 1

    if err == 0:
        for res in compare(stub_types_base, stub_types_reference):
            total_count += 1
            err = evaluate_compare_result(res, mismatches, unused_mismatches)
            if err != 0:
                failed_count += 1
                print(CHECK_FILE_ERROR.format(file_path=args.expected_mismatches))

        if unused_mismatches:
            err = 1
            print(
                "\n",
                UNUSED_DEFINITION_ERROR.format(symbols=", ".join(unused_mismatches)),
            )
            print(CHECK_FILE_ERROR.format(file_path=args.expected_mismatches))

    print(SUMMARY_MESSAGE.format(total=total_count, failed=failed_count))
    sys.exit(err)


if __name__ == "__main__":
    main()
