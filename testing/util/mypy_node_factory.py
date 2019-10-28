import os
from pathlib import Path
from typing import List, Mapping, Tuple, Type, TypeVar, cast

from mypy.nodes import Decorator, FuncDef, OverloadedFuncDef, TypeInfo, Var

from stub_analyzer import RelevantSymbolNode, get_stub_types

T = TypeVar("T")


class HandwrittenStubNotFound(Exception):
    def __init__(self, symbol_name: str, path: str):
        super().__init__(f"Handwritten stub {symbol_name} not found in {path}")


class GeneratedStubNotFound(Exception):
    def __init__(self, symbol_name: str, path: str):
        super().__init__(f"Generated stub {symbol_name} not found in {path}")


class MypyNodeFactory:
    def __init__(self) -> None:
        self._base_dir: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
        self._mypy_conf: Path = self._base_dir / "mypy.ini"
        self._handwritten_stubs_path = f"{self._base_dir}/stubs-handwritten"
        handwritten_stubs: List[RelevantSymbolNode] = list(
            get_stub_types(
                self._handwritten_stubs_path, mypy_conf_path=str(self._mypy_conf)
            )
        )

        self._generated_stubs_path = f"{self._base_dir}/stubs-generated"
        generated_stubs: List[RelevantSymbolNode] = list(
            get_stub_types(
                self._generated_stubs_path, mypy_conf_path=str(self._mypy_conf)
            )
        )

        self._handwritten_stubs_map: Mapping[str, RelevantSymbolNode] = {
            symbol.fullname(): symbol for symbol in handwritten_stubs
        }
        self._generated_stubs_map: Mapping[str, RelevantSymbolNode] = {
            symbol.fullname(): symbol for symbol in generated_stubs
        }

    def handwritten_stub_not_found(self, symbol_name: str) -> HandwrittenStubNotFound:
        return HandwrittenStubNotFound(symbol_name, self._handwritten_stubs_path)

    def generated_stub_not_found(self, symbol_name: str) -> GeneratedStubNotFound:
        return GeneratedStubNotFound(symbol_name, self._handwritten_stubs_path)

    def get(
        self, symbol_name: str, _: Type[T], raise_error: bool = True
    ) -> Tuple[T, T]:
        handwritten_symbol_node = (
            self._handwritten_stubs_map[symbol_name]
            if symbol_name in self._handwritten_stubs_map.keys()
            else None
        )
        if handwritten_symbol_node is None and raise_error:
            raise self.handwritten_stub_not_found(symbol_name)

        generated_symbol_node = (
            self._generated_stubs_map[symbol_name]
            if symbol_name in self._generated_stubs_map.keys()
            else None
        )

        if generated_symbol_node is None and raise_error:
            raise self.generated_stub_not_found(symbol_name)

        return cast(T, handwritten_symbol_node), cast(T, generated_symbol_node)

    def get_matching_func_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_function"
        return self.get(node_name, FuncDef)

    def get_missing_function_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.missing_function"
        return self.get(node_name, FuncDef, raise_error=False)

    def get_additional_args_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.additional_args"
        return self.get(node_name, FuncDef)

    def get_additional_optional_args_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.additional_optional_args"
        return self.get(node_name, FuncDef)

    def get_matching_with_arg_star(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_with_arg_star"
        return self.get(node_name, FuncDef)

    def get_matching_with_missing_arg_star(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_with_missing_arg_star"
        return self.get(node_name, FuncDef)

    def get_mismatching_with_arg_star(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.mismatching_with_arg_star"
        return self.get(node_name, FuncDef)

    def get_mismatching_with_additional_arg_star(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.mismatching_with_additional_arg_star"
        return self.get(node_name, FuncDef)

    def get_matching_with_kwarg_star2(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_with_kwarg_star2"
        return self.get(node_name, FuncDef)

    def get_matching_with_missing_kwarg_star2(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_with_missing_kwarg_star2"
        return self.get(node_name, FuncDef)

    def get_mismatching_with_kwarg_star2(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.mismatching_with_kwarg_star2"
        return self.get(node_name, FuncDef)

    def get_mismatching_with_additional_kwarg_star2(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.mismatching_with_additional_kwarg_star2"
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
