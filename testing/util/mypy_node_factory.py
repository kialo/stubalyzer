import os
from pathlib import Path
from typing import List, Tuple, Mapping, TypeVar, cast, Type

from mypy.nodes import FuncDef, OverloadedFuncDef

from stub_analyzer import RelevantSymbolNode, get_stub_types

T = TypeVar('T')


class MypyNodeFactory:
    def __init__(self) -> None:
        self._base_dir: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
        self._mypy_conf: Path = self._base_dir / "mypy.ini"

        handwritten_stubs: List[RelevantSymbolNode] = list(get_stub_types(
            f"{self._base_dir}/stubs-handwritten", mypy_conf_path=str(self._mypy_conf)
        ))

        generated_stubs: List[RelevantSymbolNode] = list(get_stub_types(
            f"{self._base_dir}/stubs-generated", mypy_conf_path=str(self._mypy_conf)
        ))

        self._handwritten_stubs_map: Mapping[str, RelevantSymbolNode] = {symbol.fullname(): symbol for symbol in handwritten_stubs}
        self._generated_stubs_map: Mapping[str, RelevantSymbolNode] = {symbol.fullname(): symbol for symbol in generated_stubs}

    def get_matching_func_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_function"
        return self.get(node_name, FuncDef)

    def get_additional_args_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.additional_args"
        return self.get(node_name, FuncDef)

    def get_additional_optional_args_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.additional_optional_args"
        return self.get(node_name, FuncDef)

    def get_overloaded_additional_args_node(self) -> Tuple[OverloadedFuncDef, OverloadedFuncDef]:
        node_name = "functions.overloaded_additional_args"
        return self.get(node_name, OverloadedFuncDef)

    def get_overloaded_additional_optional_args_node(self) -> Tuple[OverloadedFuncDef, OverloadedFuncDef]:
        node_name = "functions.overloaded_additional_optional_args"
        return self.get(node_name, OverloadedFuncDef)

    def get(self, node_name: str, _: Type[T]) -> Tuple[T, T]:
        return cast(T, self._handwritten_stubs_map[node_name]), cast(T, self._generated_stubs_map[node_name])


mypy_node_factory = MypyNodeFactory()
