import re
import sys
from argparse import ArgumentParser, Namespace
from json import loads as json_loads
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict, Generator, Iterable, Optional, Set, Tuple

from schema import Schema, SchemaError, Use

from mypy.nodes import TypeAlias, TypeVarExpr, Var
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
        "-r",
        "--reference",
        required=False,
        default=None,
        metavar="REFERENCE_STUBS",
        help="Directory of reference stubs to compare against."
        "If not specified stubgen will be used to generate the reference stubs.",
    )
    return parser.parse_args()


def compare(
    hand_written: Iterable[RelevantSymbolNode], generated: Iterable[RelevantSymbolNode]
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


def setup_expected_mismatches(
    file_path: Optional[str] = None
) -> Tuple[Dict[str, MatchResult], Set[str]]:
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
) -> bool:
    symbol = compare_result.symbol_name
    match_result = compare_result.match_result
    success = True
    expected_mismatch = mismatches.get(symbol)

    if expected_mismatch is None:
        if match_result is not MatchResult.MATCH:
            success = False
            print(f"\n{compare_result.message}")
    else:
        mismatches_left.remove(symbol)
        if match_result is MatchResult.MATCH:
            success = False
            print(
                "\n",
                MATCH_FOUND_ERROR.format(
                    symbol=symbol, mismatch_type=mismatches[symbol].value
                ),
            )
        elif match_result is not expected_mismatch:
            success = False
            print(
                "\n",
                WRONG_MISMATCH_ERROR.format(
                    symbol=symbol,
                    expected=expected_mismatch.value,
                    received=match_result.value,
                ),
            )
    return success


def generate_stub_types(base_stubs_path: str) -> Iterable[RelevantSymbolNode]:
    raise NotImplementedError("I'm working on it")


def analyze_stubs(
    mypy_conf_path: str,
    base_stubs_path: str,
    reference_stubs_path: Optional[str] = None,
    expected_mismatches_path: Optional[str] = None,
) -> bool:
    """
    Determines if the (presumably) handwritten stubs in base_stubs_path are correct;
    i.e. if they match the API of the modules that they are stubbing.
    For this they are compared to reference stubs, which by default are generated
    with mypy's stubgen tool. For each type mismatch (e.g. different function signature,
    missing class member) a message will be printed to stdout. The function will return
    False if any mismatches are found, unless they have been declared as expected.

    :param mypy_conf_path: path to mypy.ini
    :param base_stubs_path: path to the directory that contains the stubs to analyze
    :param reference_stubs_path: Path to the folder that contains the reference stubs.
        If not provided mypy's stubgen tool will be used to generate them.
    :param expected_mismatches_path: Path to JSON file that defines expected mismatches
        TODO: add/reference example of a expected_mismatches.json here
    :return: True if the stubs in base_stubs_path are considered correct
    """
    success = True
    failed_count = 0
    total_count = 0
    stub_types_base = get_stub_types(base_stubs_path, mypy_conf_path)
    if reference_stubs_path:
        stub_types_reference = get_stub_types(reference_stubs_path, mypy_conf_path)
    else:
        stub_types_reference = generate_stub_types(base_stubs_path)

    try:
        mismatches, unused_mismatches = setup_expected_mismatches(
            expected_mismatches_path
        )
    except (JSONDecodeError, SchemaError) as ex:
        print(ex, "\n", CHECK_FILE_ERROR.format(file_path=expected_mismatches_path))
        success = False

    if success:
        for res in compare(stub_types_base, stub_types_reference):
            total_count += 1
            success = evaluate_compare_result(res, mismatches, unused_mismatches)
            if not success:
                failed_count += 1
                if expected_mismatches_path:
                    print(CHECK_FILE_ERROR.format(file_path=expected_mismatches_path))

        if unused_mismatches:
            success = False
            print(
                "\n",
                UNUSED_DEFINITION_ERROR.format(symbols=", ".join(unused_mismatches)),
            )
            print(CHECK_FILE_ERROR.format(file_path=expected_mismatches_path))

    print(SUMMARY_MESSAGE.format(total=total_count, failed=failed_count))
    return success


def main() -> None:
    args = parse_command_line()
    success = analyze_stubs(
        args.config, args.stubs_handwritten, args.reference, args.expected_mismatches
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
