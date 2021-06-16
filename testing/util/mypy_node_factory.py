from typing import Dict, Tuple, Type, TypeVar, cast

from mypy.nodes import Decorator, FuncDef, OverloadedFuncDef, TypeInfo, Var

from stubalyzer import RelevantSymbolNode, get_stub_types

from .stub_config import WithStubTestConfig

T = TypeVar("T")


class HandwrittenStubNotFound(Exception):
    def __init__(self, symbol_name: str, path: str):
        super().__init__(f"Handwritten stub {symbol_name} not found in {path}")


class GeneratedStubNotFound(Exception):
    def __init__(self, symbol_name: str, path: str):
        super().__init__(f"Generated stub {symbol_name} not found in {path}")


class MypyNodeFactory(WithStubTestConfig):
    _handwritten_stubs_map: Dict[str, RelevantSymbolNode]
    _generated_stubs_map: Dict[str, RelevantSymbolNode]

    def __init__(self) -> None:
        handwritten_stubs = get_stub_types(
            self.handwritten_stubs_path,
            mypy_conf_path=self.mypy_config_path,
        )

        generated_stubs = get_stub_types(
            self.generated_stubs_path, mypy_conf_path=self.mypy_config_path
        )

        self._handwritten_stubs_map = {
            symbol.fullname: symbol for symbol, _ in handwritten_stubs
        }
        self._generated_stubs_map = {
            symbol.fullname: symbol for symbol, _ in generated_stubs
        }

    def handwritten_stub_not_found(self, symbol_name: str) -> HandwrittenStubNotFound:
        return HandwrittenStubNotFound(symbol_name, self.handwritten_stubs_path)

    def generated_stub_not_found(self, symbol_name: str) -> GeneratedStubNotFound:
        return GeneratedStubNotFound(symbol_name, self.generated_stubs_path)

    def get_generated_stubs_map(self) -> Dict[str, RelevantSymbolNode]:
        return self._generated_stubs_map

    def get_handwritten(self, symbol_name: str) -> T:
        handwritten_symbol_node = self._handwritten_stubs_map.get(symbol_name)
        if handwritten_symbol_node is None:
            raise self.handwritten_stub_not_found(symbol_name)
        return cast(T, handwritten_symbol_node)

    def get_generated(self, symbol_name: str) -> T:
        generated_symbol_node = self._generated_stubs_map.get(symbol_name)
        if generated_symbol_node is None:
            raise self.generated_stub_not_found(symbol_name)
        return cast(T, generated_symbol_node)

    def get(self, symbol_name: str, _: Type[T]) -> Tuple[T, T]:
        return self.get_handwritten(symbol_name), self.get_generated(symbol_name)

    def get_matching_func_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.matching_function"
        return self.get(node_name, FuncDef)

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

    def get_no_parameters_and_return_type_node(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.mismatching_with_no_parameters_and_no_return_type"
        return self.get(node_name, FuncDef)

    def get_function_with_no_annotation(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.function_with_no_annotation"
        return self.get(node_name, FuncDef)

    def get_function_with_args_but_no_annotation(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.function_with_args_but_no_annotation"
        return self.get(node_name, FuncDef)

    def get_overloaded_additional_args_node(
        self,
    ) -> Tuple[OverloadedFuncDef, OverloadedFuncDef]:
        node_name = "functions.overloaded_additional_args"
        return self.get(node_name, OverloadedFuncDef)

    def get_overloaded_additional_optional_args_node(
        self,
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
        self,
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

    def get_return_type_less_specific(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.return_type_less_specific"
        return self.get(node_name, FuncDef)

    def get_return_type_more_specific(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.return_type_more_specific"
        return self.get(node_name, FuncDef)

    def get_return_type_wrong(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "classes.ClassWithInvalidCustomStub.return_type_wrong"
        return self.get(node_name, FuncDef)

    def get_mislocated_methods_class(self) -> Tuple[TypeInfo, TypeInfo]:
        node_name = "classes.ClassWithoutSuperClassInHandwritten"
        return self.get(node_name, TypeInfo)

    def get_mismatch_with_zero_parameters(self) -> Tuple[FuncDef, FuncDef]:
        node_name = "functions.mismatching_with_zero_parameters"
        return self.get(node_name, FuncDef)

    def get_mislocated_method_handwritten(self) -> FuncDef:
        node_name = "classes.ClassWithoutSuperClassInHandwritten.a_method"
        return cast(FuncDef, self._handwritten_stubs_map[node_name])

    def get_missing_function_node(self) -> FuncDef:
        node_name = "functions.missing_function"
        return cast(FuncDef, self._handwritten_stubs_map[node_name])

    def get_missing_class(self) -> TypeInfo:
        node_name = "classes.MissingClass"
        return cast(TypeInfo, self._handwritten_stubs_map[node_name])

    def get_mislocated_method_actual_location_generated(self) -> FuncDef:
        node_name = "classes.AClass.a_method"
        return cast(FuncDef, self._generated_stubs_map[node_name])

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
