import os
from pathlib import Path
from typing import Dict, List

from mypy.build import BuildResult, State, build
from mypy.fscache import FileSystemCache
from mypy.main import process_options


def _mypy_analyze(mypy_conf_path: str, root_path: str, stubs_path: str) -> BuildResult:
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
    options = options.apply_changes({"mypy_path": [stubs_path]})
    return build(sources, options, None, None, fscache)


def get_stubbed_modules(graph: Dict[str, State]) -> List[State]:
    """
    Returns mypy's State for each stubbed module.
    :param graph: the result of _
    :return:
    """
    external_modules = [
        module for name, module in graph.items() if not name.startswith("kialo")
    ]
    stubbed_modules = [
        m for m in external_modules if m.tree and m.path and m.path.endswith(".pyi")
    ]
    return stubbed_modules


def _analyze_kialo() -> BuildResult:
    BACKEND_DIR = Path(os.environ["KIALO_ROOT"]) / "backend"
    BACKEND_KIALO_DIR = BACKEND_DIR / "kialo"
    STUBS_DIR = BACKEND_DIR / "stubs"
    MYPY_CONFIG_PATH = BACKEND_DIR / "mypy.ini"

    print(f"Analyzing '{BACKEND_DIR}'...")
    return _mypy_analyze(str(MYPY_CONFIG_PATH), str(BACKEND_KIALO_DIR), str(STUBS_DIR))


if __name__ == "__main__":
    # goes through all python stubs (.pyi files) and lists their exported symbols with type annotation
    graph = _analyze_kialo().graph
    for module in get_stubbed_modules(graph):
        print(module.path)

        if module.tree:
            public_symbol_names = [
                s for s in module.tree.names if not s.startswith("_")
            ]

            for symbol_name in public_symbol_names:
                symbol = module.tree.names[symbol_name]
                if symbol.module_public:
                    print(f"\t{symbol.fullname} : {symbol.type}")
