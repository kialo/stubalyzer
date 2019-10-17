import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mypy.build import BuildResult, State, build
from mypy.fscache import FileSystemCache
from mypy.main import process_options


def _mypy_analyze(
    mypy_conf_path: str, root_path: str, stubs_path: Optional[str] = None
) -> BuildResult:
    """
    Parses and analyzes the types of the code in root_path.
    :param mypy_conf_path: path to a mypy.ini
    :param root_path: path to the code directory where the type analysis is started
    :param stubs_path: path to the directory of stubs for mypy to use
    :return: Mypy's analysis result
    """
    # The call to `build.build` is inspired by `mypy/mypy/main.py::main`
    # `build` is not a documented public API, and using it requires reading mypy source.
    args = ["--config-file", mypy_conf_path, root_path]
    fscache = FileSystemCache()
    sources, options = process_options(args, fscache=fscache)
    if stubs_path is not None:
        options = options.apply_changes({"mypy_path": [stubs_path]})
    return build(sources, options, None, None, fscache)


def get_stubbed_modules(graph: Dict[str, State]) -> List[State]:
    """
    Returns mypy's State for each stubbed module.
    :param graph: the result of _
    :return:
    """
    stubbed_modules = [
        m for _, m in graph.items() if m.tree and m.path and m.path.endswith(".pyi")
    ]
    return stubbed_modules


def _analyze_stubs() -> Tuple[BuildResult, BuildResult]:
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    # CODE_DIR = BASE_DIR / "test_code"
    MYPY_CONFIG_PATH = BASE_DIR / "mypy.ini"

    return (
        _mypy_analyze(str(MYPY_CONFIG_PATH), str(BASE_DIR / "stubs-handwritten")),
        _mypy_analyze(str(MYPY_CONFIG_PATH), str(BASE_DIR / "stubs-generated")),
    )


def _print_graph_data(build_result: BuildResult) -> None:
    for module in get_stubbed_modules(build_result.graph):
        print(module.path)

        if module.tree:
            public_symbol_names = [
                s for s in module.tree.names if not s.startswith("_")
            ]

            for symbol_name in public_symbol_names:
                symbol = module.tree.names[symbol_name]
                if symbol.module_public:
                    print(f"\t{symbol.fullname} : {symbol.type}")


if __name__ == "__main__":
    # goes through all python stubs (.pyi files) and lists their exported symbols with type annotation
    hand, gen = _analyze_stubs()

    _print_graph_data(hand)

    print()
    print()
    print("------------------------------------")
    print()
    print()

    _print_graph_data(gen)
