import re
import sys
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from collections import defaultdict
from enum import Enum
from importlib.util import find_spec
from io import StringIO
from json import loads as json_loads
from json.decoder import JSONDecodeError
from os import linesep, scandir
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from traceback import format_exception
from typing import (
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
)
from xml.etree.ElementTree import Element, ElementTree, SubElement

from mypy.nodes import TypeAlias, TypeVarExpr, Var
from mypy.stubgen import generate_stubs, parse_options
from schema import Or, Schema, SchemaError, Use

from .collect import get_stub_types
from .compare import ComparisonResult, MatchResult, compare_symbols
from .lookup import lookup_symbol
from .types import RelevantSymbolNode

EXPECTED_MISMATCH_SCHEMA = Schema(Or({}, {str: Use(MatchResult.declare_mismatch)}))
CHECK_FILE_ERROR = 'Check "{file_path}" to fix.'
MATCH_FOUND_ERROR = (
    'Expected "{symbol}" to be "{mismatch_type}" but it matched.'
    f"{linesep}{CHECK_FILE_ERROR}"
)
WRONG_MISMATCH_ERROR = (
    'Expected "{symbol}" to be "{expected}" but it was "{received}".'
    f"{linesep}{CHECK_FILE_ERROR}"
)
UNUSED_DEFINITION_ERROR = (
    "Expected the following symbols to fail, "
    f"but they were not processed:{linesep}"
    "{symbols}"
    f"{linesep}{CHECK_FILE_ERROR}"
)
FILE_NOT_FOUND_WARNING = (
    'WARNING: Provided file for expected mismatches ("{file_path}") not found.'
)
SUCCESS_MESSAGE = "Successfully validated {total} stubs."
FAIL_MESSAGE = "Failure: {failed} of {total} stubs seem not to be valid."
IGNORE_MESSAGE = (
    "{ignored} fail(s) were ignored, "
    "because they were defined to be expected mismatches."
)


class EvaluationResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    EXPECTED_FAILURE = "expected_failure"


def write_error(
    *messages: str, sep: str = "", symbol: Optional[RelevantSymbolNode] = None
) -> None:
    sys.stderr.write(sep.join(messages))
    sys.stderr.write(linesep)


def parse_command_line() -> Namespace:
    parser = ArgumentParser(
        description=dedent(
            """\
        Analyze a set of (handcrafted) mypy stubs by comparing them to (generated)
        reference stubs
        """
        ),
        formatter_class=RawTextHelpFormatter,
    )
    required_group = parser.add_argument_group("required arguments")
    required_group.add_argument(
        "-c", "--config", required=True, help="Mypy config file"
    )
    parser.add_argument(
        "-e",
        "--expected-mismatches",
        required=False,
        default=None,
        help=dedent(
            """\
        A JSON file, which defines expected mismatching
        symbols and their match results. If any symbol is
        declared in an expected_mismatches JSON file,
        %(prog)s will count it as an expected failure, and
        ignore this inconsistency.

        Example contents:
        {
            "my.module.function: "mismatch",
            "another.module.Class: "not_found"
        }

        According to the example above, we expect the signature
        of my.module.function to mismatch, and module.Class to
        be missing in the generated stubs. %(prog)s will
        ignore these inconsistencies.
        """
        ),
    )
    parser.add_argument(
        dest="stubs_handwritten",
        metavar="STUBS_HANDWRITTEN",
        help=dedent(
            """\
        Directory of handwritten stubs that need to be
        analyzed
        """
        ),
    )
    parser.add_argument(
        "-r",
        "--reference",
        required=False,
        default=None,
        metavar="REFERENCE_STUBS",
        help=dedent(
            """
        Directory of reference stubs to compare against. If
        not specified stubgen will be used to generate the
        reference stubs.
        """
        ),
    )
    parser.add_argument(
        "-x",
        "--checkstyle-report",
        required=False,
        default=None,
        help=dedent(
            """
        Write an xml report in checkstyle format to the given file.
        """
        ),
    )
    parser.add_argument(
        "-s",
        "--silent",
        required=False,
        default=False,
        action="store_true",
        help=dedent(
            """
        Suppress all non-error output.
        """
        ),
    )
    parser.add_argument(
        "-p",
        "--include-private",
        required=False,
        default=False,
        action="store_true",
        help=dedent(
            """
        Include definitions stubgen would otherwise consider
        private, when generating the reference stubs. (e.g.
        names with a single leading underscore, like "_foo")
        """
        ),
    )
    return parser.parse_args()


def compare(
    hand_written: Iterable[RelevantSymbolNode], generated: Iterable[RelevantSymbolNode]
) -> Generator[ComparisonResult, None, None]:
    """Compare hand written to generated stubs."""
    gen_map: Dict[str, RelevantSymbolNode] = {
        symbol.fullname: symbol for symbol in generated
    }

    for symbol in hand_written:
        name = symbol.fullname
        if name in gen_map:
            yield compare_symbols(symbol, gen_map[name])
        elif isinstance(symbol, (TypeAlias, TypeVarExpr, Var)) and re.match(
            r"_[^_].*", name.split(".")[-1]
        ):
            # Ignore symbols that begin with (exactly) one _,
            # since we assume they are private
            continue
        else:
            lookup_result = lookup_symbol(gen_map, symbol)
            generated_symbol = lookup_result.symbol
            if generated_symbol:
                yield ComparisonResult.create_mislocated_symbol(
                    symbol=symbol,
                    reference=generated_symbol,
                    data={"containing_class": lookup_result.containing_class},
                )
            else:
                yield ComparisonResult.create_not_found(symbol)


def setup_expected_mismatches(
    file_path: Optional[str] = None,
) -> Tuple[Dict[str, MatchResult], Set[str]]:
    if not file_path:
        return dict(), set()

    mismatches: Dict[str, MatchResult] = {}
    mismatches_file = Path(file_path)
    if not mismatches_file.exists():
        write_error(FILE_NOT_FOUND_WARNING.format(file_path=file_path))
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
    expected_mismatches_path: Optional[str] = None,
    *,
    loggers: List[Callable[..., None]],
) -> EvaluationResult:
    symbol = compare_result.symbol
    symbol_name = compare_result.symbol_name
    match_result = compare_result.match_result
    evaluation_result = EvaluationResult.SUCCESS
    expected_mismatch = mismatches.get(symbol_name)

    if expected_mismatch is None:
        if match_result is not MatchResult.MATCH:
            evaluation_result = EvaluationResult.FAILURE
            for logger in loggers:
                logger(
                    linesep,
                    compare_result.message,
                    symbol=symbol,
                )
    else:
        mismatches_left.remove(symbol_name)
        if match_result is MatchResult.MATCH:
            evaluation_result = EvaluationResult.FAILURE
            assert expected_mismatches_path
            for logger in loggers:
                logger(
                    linesep,
                    MATCH_FOUND_ERROR.format(
                        symbol=symbol_name,
                        mismatch_type=mismatches[symbol_name].value,
                        file_path=expected_mismatches_path,
                    ),
                    symbol=symbol,
                )
        elif match_result is not expected_mismatch:
            evaluation_result = EvaluationResult.FAILURE
            assert expected_mismatches_path
            for logger in loggers:
                logger(
                    linesep,
                    WRONG_MISMATCH_ERROR.format(
                        symbol=symbol_name,
                        expected=expected_mismatch.value,
                        received=match_result.value,
                        file_path=expected_mismatches_path,
                    ),
                    symbol=symbol,
                )
        else:
            evaluation_result = EvaluationResult.EXPECTED_FAILURE
    return evaluation_result


def call_stubgen(command_line_args: List[str]) -> None:
    """
    Call stubgen like the command line tool.

    :param command_line_args: list of command line args
    """

    generate_stubs(parse_options(command_line_args))


def silence_output() -> Tuple[StringIO, StringIO]:
    """Redirect all output to in-memory buffers instead of stdout and stderr."""
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    return (sys.stdout, sys.stderr)


def restore_output() -> None:
    """Restore output of stdout and stderr to defaults."""
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


def generate_stub_types(
    base_stubs_path: str,
    mypy_conf_path: str,
    silent: bool = False,
    include_private: bool = False,
) -> Iterable[Tuple[RelevantSymbolNode, str]]:
    """
    Use stubgen to generate reference stub types of the modules stubbed in
    base_stubs_path. For this to work the modules need to be installed.

    :param base_stubs_path: path to directory with (handwritten) stubs
    :param mypy_conf_path: path to mypy.ini
    :return: returns the reference stub types
    """
    with TemporaryDirectory() as reference_stubs_path:
        packages = [
            entry.name.replace(".pyi", "")
            for entry in scandir(base_stubs_path)
            if entry.is_dir() or entry.name.endswith(".pyi")
        ]
        for package in packages:
            if find_spec(package) is None:
                print(
                    f'Error: The package "{package}" is not installed. Therefore no '
                    f"reference stubs can be generated for it automatically. Use the "
                    f"option -r to provide the reference stubs manually, or install "
                    f"the package."
                )
                sys.exit(1)
            try:
                if silent:
                    silence_output()
                default_parameters = [
                    "--ignore-errors",
                    "-q",
                    "-p",
                    package,
                    "-o",
                    reference_stubs_path,
                ]
                call_stubgen(
                    ["--include-private"] + default_parameters
                    if include_private
                    else default_parameters
                )
                if silent:
                    restore_output()
            except Exception as ex:
                restore_output()
                write_error(
                    f'Error: Generating stubs for the package "{package}" failed:',
                    linesep,
                    *format_exception(type(ex), ex, ex.__traceback__),
                )

        return list(get_stub_types(reference_stubs_path, mypy_conf_path))


class ErrorEntry(NamedTuple):
    symbol: RelevantSymbolNode
    message: str


class CheckStyleWriter:
    def __init__(self, path_map: Dict[RelevantSymbolNode, str]):
        self.path_map = path_map
        self.errors_by_file: Dict[str, List[ErrorEntry]] = defaultdict(list)

    def collect_error(
        self, *messages: str, sep: str = "", symbol: RelevantSymbolNode
    ) -> None:
        message = sep.join(messages)
        path = self.path_map[symbol]
        self.errors_by_file[path].append(ErrorEntry(symbol=symbol, message=message))

    def build_tree(self) -> ElementTree:
        root = Element("checkstyle", {"version": "4.3"})
        for filename in sorted(self.errors_by_file.keys()):
            errors = self.errors_by_file[filename]
            file = SubElement(root, "file", {"name": filename})
            for error in sorted(errors, key=lambda x: (x.symbol.line, x.symbol.column)):
                SubElement(
                    file,
                    "error",
                    {
                        "line": str(error.symbol.line),
                        "column": str(error.symbol.column),
                        "severity": "error",
                        "message": error.message,
                    },
                )
        return ElementTree(root)


def analyze_stubs(
    mypy_conf_path: str,
    base_stubs_path: str,
    reference_stubs_path: Optional[str] = None,
    expected_mismatches_path: Optional[str] = None,
    checkstyle_report: Optional[str] = None,
    silent: bool = False,
    include_private: bool = False,
) -> bool:
    """
    Determine if the (presumably) handwritten stubs in base_stubs_path are correct;
    i.e. if they match the API of the modules that they are stubbing.

    For this they are compared to reference stubs, which by default are generated
    with mypy's stubgen tool. For each type mismatch (e.g. different function signature,
    missing class member) a message will be printed to stdout. The function will return
    False if any mismatches are found, unless they have been declared as expected.

    :param mypy_conf_path: path to mypy.ini
    :param base_stubs_path: path to the directory that contains the stubs to analyze
    :param reference_stubs_path: Path to the folder that contains the reference stubs.
        If not provided mypy's stubgen tool will be used to generate them.
    :param expected_mismatches_path: Path to JSON file that defines expected mismatches.
        Example:

        .. code-block:: json

            {
                "my.module.function": "mismatch",
                "another.module.Class": "not_found"
            }
    :param checkstyle_report: if this path is given, a xml report in checkstyle format
        will be written.
    :param silent: Suppress all non-error output.
    :param include_private: Call stubgen with --include-private.
    :return: True if the stubs in base_stubs_path are considered correct
    """
    success = True
    failed_count = 0
    total_count = 0
    expected_count = 0

    try:
        mismatches, unused_mismatches = setup_expected_mismatches(
            expected_mismatches_path
        )
    except (JSONDecodeError, SchemaError) as ex:
        write_error(
            str(ex),
            linesep,
            CHECK_FILE_ERROR.format(file_path=expected_mismatches_path),
        )
        success = False

    if success:
        # Prevent overloaded function definitions from appearing multiple times
        stub_types_base_map = {
            symbol: path
            for (symbol, path) in get_stub_types(base_stubs_path, mypy_conf_path)
        }
        if reference_stubs_path:
            stub_types_reference = set(
                stub for stub, _ in get_stub_types(reference_stubs_path, mypy_conf_path)
            )
        else:
            stub_types_reference = set(
                stub
                for stub, _ in generate_stub_types(
                    base_stubs_path, mypy_conf_path, silent, include_private
                )
            )
        checkstyle_writer = CheckStyleWriter(stub_types_base_map)
        for res in compare(stub_types_base_map.keys(), stub_types_reference):
            total_count += 1
            evaluation_result = evaluate_compare_result(
                res,
                mismatches,
                unused_mismatches,
                expected_mismatches_path,
                loggers=[write_error, checkstyle_writer.collect_error],
            )
            if evaluation_result is EvaluationResult.FAILURE:
                failed_count += 1
            elif evaluation_result is EvaluationResult.EXPECTED_FAILURE:
                expected_count += 1
        success = failed_count == 0

        if checkstyle_report:
            checkstyle_tree = checkstyle_writer.build_tree()
            checkstyle_tree.write(
                checkstyle_report, encoding="UTF-8", xml_declaration=True
            )

        if unused_mismatches:
            success = False
            symbols = linesep.join([f" - {mm}" for mm in unused_mismatches])
            write_error(
                linesep,
                UNUSED_DEFINITION_ERROR.format(
                    symbols=symbols, file_path=expected_mismatches_path
                ),
            )

    ignore_message = IGNORE_MESSAGE.format(ignored=expected_count)

    if success:
        summary = SUCCESS_MESSAGE.format(total=total_count)
        if not silent:
            print(
                "", summary, (ignore_message if expected_count > 0 else ""), sep=linesep
            )
    else:
        summary = FAIL_MESSAGE.format(total=total_count, failed=failed_count)
        write_error(
            "", summary, (ignore_message if expected_count > 0 else ""), sep=linesep
        )
    return success


def main() -> None:
    args = parse_command_line()
    success = analyze_stubs(
        args.config,
        args.stubs_handwritten,
        args.reference,
        args.expected_mismatches,
        args.checkstyle_report,
        args.silent,
        args.include_private,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
