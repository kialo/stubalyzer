"""
API for analyzing Python stubs using mypy.
"""
from os.path import abspath
from typing import Any, Dict, Generator, NamedTuple, Optional, Set, Union

from mypy.build import BuildResult, State, build
from mypy.fscache import FileSystemCache
from mypy.main import process_options
from mypy.meet import is_overlapping_types
from mypy.nodes import (
    CONTRAVARIANT,
    COVARIANT,
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
from mypy.types import Type as TypeNode

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
        # the symbol represents a function definition,
        # variable, type alias or generic TypeVar
        yield symbol_node
    else:
        assert False, f"Unexpected symbol type {type(symbol_node)}"


def get_stub_types(
    stubs_path: str, mypy_conf_path: str, root_path: Optional[str] = None
) -> Generator[RelevantSymbolNode, None, None]:
    """
    Analyzes the stub files in stubs_path and returns module
    and class definitions of stubs as symbol nodes.
    Only relevant symbol nodes (e.g. for variables, functions, classes, methods)
    are returned.
    They contain the type annotation information.

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


def _mypy_types_match(a: TypeNode, b: TypeNode) -> bool:
    return is_overlapping_types(a, b) or is_subtype(a, b)


def _compare_mypy_types(
    a: RelevantSymbolNode,
    b: RelevantSymbolNode,
    a_type: Optional[TypeNode],
    b_type: Optional[TypeNode],
) -> ComparisonResult:
    if b_type is None:
        # Mypy does not have enought type information
        # so we accept that our stub is correct
        return ComparisonResult.create_match(
            type_a=a, type_b=b, message="Generated type is None"
        )

    if a_type is None:
        return ComparisonResult.create_mismatch(type_a=a, type_b=b)

    if _mypy_types_match(a_type, b_type):
        return ComparisonResult.create_match(
            type_a=a,
            type_b=b,
            data={
                "a_name": fullname(a),
                "a_type": a_type,
                "b_name": fullname(b),
                "b_type": b_type,
                "overlap": is_overlapping_types(a_type, b_type),
                "subtype": is_subtype(a_type, b_type),
            },
        )

    return ComparisonResult.create_mismatch(type_a=a, type_b=b)


def _compare_type_infos(a: TypeInfo, b: TypeInfo) -> ComparisonResult:
    """Compare TypeInfo nodes, which are class definitions.

    Currently only does a comparison on the fullname, since we only
    care that the class is defined at the same location under the same name.
    """
    if a.fullname() == b.fullname():
        return ComparisonResult.create_match(type_a=a, type_b=b)
    else:
        return ComparisonResult.create_mismatch(type_a=a, type_b=b)


def _compare_type_aliases(a: TypeAlias, b: TypeAlias) -> ComparisonResult:
    """Compare TypeAlias nodes.

    TypeAlias nodes contain the referenced type as the target.
    """
    return _compare_mypy_types(a, b, a.target, b.target)


def _format_type_var(x: TypeVarExpr) -> str:
    """Format a TypeVarExpr as it would be written in code."""
    variance = ""
    if x.variance == COVARIANT:
        variance = ", covariant=True"
    elif x.variance == CONTRAVARIANT:
        variance = ", contravariant=True"

    values = ""
    if x.values:
        values = ", " + (", ".join(str(t) for t in x.values))

    return f"{x.name} = TypeVar('{x.name}'{values}{variance})"


def _compare_type_var_expr(a: TypeVarExpr, b: TypeVarExpr) -> ComparisonResult:
    raise NotImplementedError(
        "Comparison of type variables (TypeVarExpr) is not implemented"
        f"\n{_format_type_var(a)}"
        f"\n{_format_type_var(b)}"
    )


def compare_symbols(a: RelevantSymbolNode, b: RelevantSymbolNode) -> ComparisonResult:
    """Check if symbol node a is compatible with b."""
    print(f"Comparing {a.fullname()}")

    # TODO: Check if this is always the case, i.e. could there be
    # cases where a and b don't have the same class but still match?
    if type(a) != type(b):
        return ComparisonResult.create_mismatch(type_a=a, type_b=b)

    if isinstance(a, TypeInfo) and isinstance(b, TypeInfo):
        return _compare_type_infos(a, b)

    if isinstance(a, TypeAlias) and isinstance(b, TypeAlias):
        return _compare_type_aliases(a, b)

    if isinstance(a, TypeVarExpr) and isinstance(b, TypeVarExpr):
        return _compare_type_var_expr(a, b)

    return _compare_mypy_types(a, b, getattr(a, "type"), getattr(b, "type"))


def resolve_generated_symbol(
    symbol: RelevantSymbolNode, gen_map: Dict[str, RelevantSymbolNode]
) -> Optional[RelevantSymbolNode]:
    """Resolve the given symbol in the generated stubs.

    TODO: Inline"""
    return gen_map.get(symbol.fullname())
