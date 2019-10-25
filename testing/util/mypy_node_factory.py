import os
from pathlib import Path
from typing import List, Mapping, Tuple, Type, TypeVar, cast

from mypy.nodes import Decorator, FuncDef, OverloadedFuncDef, TypeInfo, Var

from stub_analyzer import RelevantSymbolNode, get_stub_types

T = TypeVar("T")


class MypyNodeFactory:
    def __init__(self) -> None:
        self._base_dir: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
        self._mypy_conf: Path = self._base_dir / "mypy.ini"

        handwritten_stubs: List[RelevantSymbolNode] = list(
            get_stub_types(
                f"{self._base_dir}/stubs-handwritten",
                mypy_conf_path=str(self._mypy_conf),
            )
        )

        generated_stubs: List[RelevantSymbolNode] = list(
            get_stub_types(
                f"{self._base_dir}/stubs-generated", mypy_conf_path=str(self._mypy_conf)
            )
        )

        self._handwritten_stubs_map: Mapping[str, RelevantSymbolNode] = {
            symbol.fullname(): symbol for symbol in handwritten_stubs
        }
        self._generated_stubs_map: Mapping[str, RelevantSymbolNode] = {
            symbol.fullname(): symbol for symbol in generated_stubs
        }

    def get(self, node_name: str, _: Type[T]) -> Tuple[T, T]:
        return (
            cast(T, self._handwritten_stubs_map[node_name]),
            cast(T, self._generated_stubs_map[node_name]),
        )

    def get_matching_func_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_function"
        return self.get(node_name, FuncDef)

    def get_additional_args_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.additional_args"
        return self.get(node_name, FuncDef)

    def get_additional_optional_args_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.additional_optional_args"
        return self.get(node_name, FuncDef)

    def get_overloaded_additional_args_node(
        self
    ) -> Tuple[OverloadedFuncDef, OverloadedFuncDef]:
        node_name = "functions.overloaded_additional_args"
        return self.get(node_name, OverloadedFuncDef)

    def get_overloaded_additional_optional_args_node(
        self
    ) -> Tuple[OverloadedFuncDef, OverloadedFuncDef]:
        node_name = "functions.overloaded_additional_optional_args"
        return self.get(node_name, OverloadedFuncDef)

    def get_decorated_function(self) -> Tuple[Decorator, Decorator]:
        node_name = "functions.decorated_function"
        return self.get(node_name, Decorator)

    def get_decorated_with_additional_args(self) -> Tuple[Decorator, Decorator]:
        node_name = "functions.decorated_with_additional_args"
        return self.get(node_name, Decorator)

    def get_decorated_with_additional_optional_args(
        self
    ) -> Tuple[Decorator, Decorator]:
        node_name = "functions.decorated_with_additional_optional_args"
        return self.get(node_name, Decorator)

    def get_class(self) -> Tuple[TypeInfo, TypeInfo]:
        node_name = "classes.AClass"
        return self.get(node_name, TypeInfo)

    def get_another_class(self) -> Tuple[TypeInfo, TypeInfo]:
        node_name = "classes.AnotherClass"
        return self.get(node_name, TypeInfo)

    def get_method(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.AClass.a_method"
        return self.get(node_name, FuncDef)

    def get_classmethod(self) -> Tuple[Decorator, Decorator]:
        node_name = "classes.AClass.a_classmethod"
        return self.get(node_name, Decorator)

    def get_overridden_method(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.OverridingMethod.overwritten"
        return self.get(node_name, FuncDef)

    def get_overridden_classmethod(self) -> Tuple[Decorator, Decorator]:
        node_name = "classes.OverridingClassmethod.overwritten"
        return self.get(node_name, Decorator)

    def get_argument_order_wrong(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.argument_order_wrong"
        return self.get(node_name, FuncDef)

    def get_argument_names_wrong(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.argument_names_wrong"
        return self.get(node_name, FuncDef)

    def get_argument_types_wrong(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.argument_types_wrong"
        return self.get(node_name, FuncDef)

    def get_argument_types_less_specific(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.argument_types_less_specific"
        return self.get(node_name, FuncDef)

    def get_return_type_less_specific(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.return_type_less_specific"
        return self.get(node_name, FuncDef)

    def get_return_type_wrong(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.return_type_wrong"
        return self.get(node_name, FuncDef)

    def get_any_var(self) -> Var:
        node_name = "vars.any_var"
        return cast(Var, self._handwritten_stubs_map[node_name])

    def get_int_var(self) -> Var:
        node_name = "vars.int_var"
        return cast(Var, self._handwritten_stubs_map[node_name])

    def get_bool_var(self) -> Var:
        node_name = "vars.bool_var"
        return cast(Var, self._handwritten_stubs_map[node_name])

    def get_str_var(self) -> Var:
        node_name = "vars.str_var"
        return cast(Var, self._handwritten_stubs_map[node_name])


mypy_node_factory = MypyNodeFactory()
