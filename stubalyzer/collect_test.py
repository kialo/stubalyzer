from typing import Dict, cast

from mypy.nodes import Decorator, SymbolNode, TypeAlias, TypeInfo
from mypy.types import CallableType, FuncDef, Instance, UnboundType, UnionType

from testing.util import WithStubTestConfig

from .collect import get_stub_types


class WithStubSymbols(WithStubTestConfig):
    _symbols: Dict[str, SymbolNode]

    @classmethod
    def setup_class(cls) -> None:
        stubs_path = cls.get_generated_stubs_path()
        conf_path = cls.get_mypy_config_path()

        cls._symbols = {
            s.fullname: s for (s, _) in get_stub_types(str(stubs_path), str(conf_path))
        }

    @property
    def symbols(self) -> Dict[str, SymbolNode]:
        return self._symbols


class TestGetStubTypes(WithStubSymbols):
    def test_method_stub(self) -> None:
        method = cast(
            FuncDef,
            self.symbols[
                "classes.ClassWithInvalidCustomStub.return_type_less_specific"
            ],
        )

        # function arguments
        assert method.arg_names == ["self", "foo", "bar"]
        assert method.arguments[0].type_annotation is None

        int_param = cast(UnboundType, method.arguments[1].type_annotation)
        assert isinstance(int_param, UnboundType)
        assert int_param.name == "int"

        # function return value
        assert isinstance(method.type, CallableType)
        assert isinstance(method.type.ret_type, Instance)
        assert method.type.ret_type.type.name == "bool"

    def test_type_alias(self) -> None:
        type_alias = cast(TypeAlias, self.symbols["type_aliases.Strint"])
        assert isinstance(type_alias, TypeAlias)
        assert type_alias.name == "Strint"
        assert isinstance(type_alias.target, UnionType)

        assert str(type_alias.target.items[0]) == "builtins.str"
        assert str(type_alias.target.items[1]) == "builtins.int"

    def test_inheritance(self) -> None:
        subclass = self.symbols["classes.SubClassOfAClass"]
        assert subclass
        assert isinstance(subclass, TypeInfo)
        assert {b.type.fullname for b in subclass.bases} == {"classes.AClass"}

    def test_inherited_definitions(self) -> None:
        another_class = self.symbols.get("classes.SubClassOfAClass")
        assert isinstance(another_class, TypeInfo)

        # the hash method is not declared in the bcrypt class directly
        assert not another_class.names.get("a_classmethod")
        assert "classes.SubClassOfAClass.a_classmethod" not in self.symbols

        # but it can be resolved from definitions inherited from base classes
        a_classmethod = another_class.get("a_classmethod")
        assert a_classmethod and isinstance(a_classmethod.node, Decorator)

    def test_base_classes(self) -> None:
        subClassOfAClass = self.symbols.get("classes.SubClassOfAClass")
        assert isinstance(subClassOfAClass, TypeInfo)
        assert {b.type.fullname for b in subClassOfAClass.bases} == {"classes.AClass"}

        aClass = self.symbols.get("classes.AClass")
        assert isinstance(aClass, TypeInfo)
        assert {b.type.fullname for b in aClass.bases} == {"builtins.object"}
