"""
API for analyzing Python stubs using mypy.
"""
from os.path import abspath
from typing import Any, Dict, Generator, NamedTuple, Optional, Set, Type, Union

from mypy.build import BuildResult, State, build
from mypy.fscache import FileSystemCache
from mypy.main import process_options
from mypy.meet import is_overlapping_types
from mypy.nodes import (
    GDEF,
    MDEF,
    Decorator,
    FuncDef,
    MypyFile,
    OverloadedFuncDef,
    SymbolNode,
    TypeAlias,
    TypeInfo,
    TypeVarExpr,
    Var,
)
from mypy.subtypes import is_subtype

RelevantSymbolNode = Union[
    Decorator, FuncDef, OverloadedFuncDef, Var, TypeInfo, TypeVarExpr, TypeAlias
]
"""
SymbolNodes that are interesting for stub files.
Excludes MypyFiles (the modules themselves), imported names and Mypy placeholders
"""


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
    # `build` is not a documented public API
    args = ["--config-file", mypy_conf_path, root_path]
    fscache = FileSystemCache()
    sources, options = process_options(args, fscache=fscache)
    if stubs_path is not None:
        options = options.apply_changes({"mypy_path": [stubs_path]})
    return build(sources, options, None, None, fscache)


def is_stubbed_module(module: State) -> bool:
    return module.path is not None and module.path.endswith(".pyi")


def collect_types(
    symbol_node: SymbolNode, collected_types: Optional[Set[str]] = None
) -> Generator[RelevantSymbolNode, None, None]:
    """
    Collects all relevant type definitions of the symbols in the given node.
    :param symbol_node: any symbol node, e.g. MypyFile (BuildResult.graph.tree)
    :param collected_types: used to avoid collecting duplicates
    """
    if not collected_types:
        collected_types = set()

    # ignore builtins because we don't provide stubs for them
    if "builtins" in symbol_node.fullname():
        return

    # do not collect types twice
    if symbol_node.fullname() in collected_types:
        return
    collected_types.add(symbol_node.fullname())

    if isinstance(symbol_node, MypyFile):
        # the symbol node represents a Python module
        for symbol in symbol_node.names.values():
            # only global and class member definitions are interesting
            if symbol.kind not in [GDEF, MDEF]:
                pass

            if symbol.node and symbol.module_public:
                yield from collect_types(symbol.node, collected_types)
    elif isinstance(symbol_node, TypeInfo):
        # the symbol represents a class definition
        yield symbol_node
        for class_member in symbol_node.names.values():
            if class_member.node:
                yield from collect_types(class_member.node, collected_types)
    elif isinstance(
        symbol_node,
        (Decorator, FuncDef, OverloadedFuncDef, Var, TypeAlias, TypeVarExpr),
    ):
        # the symbol represents a function definition, variable, type alias or generic TypeVar
        yield symbol_node
    else:
        assert False, f"Unexpected symbol type {type(symbol_node)}"


def get_stub_types(
    stubs_path: str, mypy_conf_path: str, root_path: Optional[str] = None
) -> Generator[RelevantSymbolNode, None, None]:
    """
    Analyzes the stub files in stubs_path and returns module and class definitions of stubs as symbol nodes.
    Only relevant symbol nodes (e.g. for variables, functions, classes, methods) are returned. They contain the
    type annotation information.
    :param stubs_path: where all the stub files are located
    :param mypy_conf_path: path to mypy.ini
    :param root_path: path to the code directory where the type analysis is started
    """
    stubs_path = abspath(stubs_path)

    if root_path:
        build_result = _mypy_analyze(mypy_conf_path, root_path, stubs_path)
    else:
        build_result = _mypy_analyze(mypy_conf_path, stubs_path)

    stubbed_modules = {
        module
        for module in build_result.graph.values()
        if module.path
        and is_stubbed_module(module)
        and module.path.startswith(stubs_path)
    }

    for module in stubbed_modules:
        if module.tree:
            yield from collect_types(module.tree)


def fullname(x: Any) -> Optional[str]:
    attr = getattr(x, "fullname", None)
    if callable(attr):
        return str(attr())
    else:
        return str(attr)


class ComparisonResult(NamedTuple):
    type_a: RelevantSymbolNode
    type_b: RelevantSymbolNode
    match: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def create_mismatch(
        cls,
        type_a: RelevantSymbolNode,
        type_b: RelevantSymbolNode,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ComparisonResult":
        return cls(
            type_a=type_a,
            type_b=type_b,
            match=False,
            message=(
                message
                or (
                    f"Types of {fullname(type_a)} ({type(type_a)},"
                    f" {getattr(type_a, 'type', None)})"
                    f" and {fullname(type_b)} ({type(type_b)},"
                    f" {getattr(type_b, 'type', None)}) do not match."
                )
            ),
            data=data,
        )

    @classmethod
    def create_match(
        cls,
        type_a: RelevantSymbolNode,
        type_b: RelevantSymbolNode,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "ComparisonResult":
        return cls(
            type_a=type_a,
            type_b=type_b,
            match=True,
            message=(
                message
                or (
                    f"Types of {fullname(type_a)} ({type(type_a)},"
                    " {getattr(type_a, 'type', None)})"
                    f" and {fullname(type_b)} ({type(type_b)},"
                    " {getattr(type_b, 'type', None)}) match."
                )
            ),
            data=data,
        )


def _compare_other(a: RelevantSymbolNode, b: RelevantSymbolNode) -> ComparisonResult:
    raise ComparisonResult.create_mismatch(
        type_a=a,
        type_b=b,
        message=f"Don't know what to do with types {a.__name__}, {b.__name__}",
    )


def _mypy_types_match(a: Type, b: Type) -> bool:
    return is_overlapping_types(a, b) or is_subtype(a, b)


def is_classmethod_decorator(node: RelevantSymbolNode) -> bool:
    return isinstance(node, Decorator) and (
        node.func.is_class or node.var.is_classmethod
    )


def _compare_mypy_types(
    a: RelevantSymbolNode, b: RelevantSymbolNode
) -> ComparisonResult:
    if a.type is None and b.type is None:
        return ComparisonResult.create_match(type_a=a, type_b=b)
    if (a.type is None or b.type is None) and a.type is not b.type:
        return ComparisonResult.create_mismatch(type_a=a, type_b=b)

    if _mypy_types_match(a.type, b.type):
        return ComparisonResult.create_match(
            type_a=a,
            type_b=b,
            message=(
                f"Types of {fullname(a)} ({a.type}) and {fullname(b)} ({b.type}) match,"
                f" (overlap: {is_overlapping_types(a.type, b.type)})"
                f" (subtype: {is_subtype(a.type, b.type)})"
            ),
        )

    if is_classmethod_decorator(a) and is_classmethod_decorator(b):
        a_modified_type = a.type.copy_modified(
            arg_types=a.type.arg_types[1:],
            arg_kinds=a.type.arg_kinds[1:],
            arg_names=a.type.arg_names[1:],
        )
        b_modified_type = b.type.copy_modified(
            arg_types=b.type.arg_types[1:],
            arg_kinds=b.type.arg_kinds[1:],
            arg_names=b.type.arg_names[1:],
        )
        if _mypy_types_match(a_modified_type, b_modified_type):
            return ComparisonResult.create_match(
                type_a=a,
                type_b=b,
                message=(
                    f"Types of {fullname(a)} and {fullname(b)} match"
                    f" after removing 'cls' argument."
                ),
                data={
                    "a_modified_type": a_modified_type,
                    "b_modified_type": b_modified_type,
                },
            )

    return ComparisonResult.create_mismatch(type_a=a, type_b=b)


def _compare_type_infos(a: TypeInfo, b: TypeInfo) -> ComparisonResult:
    if fullname(a) == fullname(b):
        return ComparisonResult.create_match(type_a=a, type_b=b)
    else:
        return ComparisonResult.create_mismatch(type_a=a, type_b=b)


def compare_types(a: RelevantSymbolNode, b: RelevantSymbolNode) -> ComparisonResult:
    if hasattr(a, "type"):
        if not hasattr(b, "type"):
            return ComparisonResult.create(type_a=a, type_b=b)

        return _compare_mypy_types(a, b)
    else:
        if isinstance(a, TypeInfo):
            if not isinstance(b, TypeInfo):
                return ComparisonResult.create(type_a=a, type_b=b)

            return _compare_type_infos(a, b)
        elif isinstance(b, TypeInfo):
            return ComparisonResult.create(type_a=a, type_b=b)
        else:
            return _compare_other(a, b)
