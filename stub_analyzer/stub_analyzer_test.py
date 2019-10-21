import builtins
from os.path import abspath, dirname
from pathlib import Path
from typing import Dict, cast
from unittest.mock import Mock

from mypy.build import State
from mypy.nodes import Decorator, FuncDef, SymbolNode, TypeAlias, TypeInfo
from mypy.types import Any, AnyType, CallableType, Instance, UnboundType, UnionType

from stub_analyzer.api import get_stub_types, should_include_module

from .stub_analyzer import main


def module(path: str) -> State:
    return Mock(State, path=path)


def get_stub_types_dict(stub_folder: str) -> Dict[str, SymbolNode]:
    package_path = Path(dirname(abspath(__file__))).parent
    stubs_path = (package_path / stub_folder).absolute()
    conf_path = (package_path / "mypy.ini").absolute()

    assert stubs_path.exists()
    assert conf_path.exists()

    return {s.fullname(): s for s in get_stub_types(str(stubs_path), str(conf_path))}


class TestShouldIncludeModule:
    def test_excludes_external(self) -> None:
        assert not should_include_module(module("path/to/typeshed/module.pyi"))
        assert not should_include_module(module("site-packages/mypy/some.pyi"))
        assert not should_include_module(module("path/to/builtins.pyi"))
        assert should_include_module(module("some/other/module.pyi"))
        assert should_include_module(module("stubs-handwritten/passlib/__init__.pyi"))


class TestGetStubTypesWithHandwrittenStubs:
    symbols: Dict[str, SymbolNode]

    @classmethod
    def setup_class(cls) -> None:
        cls.symbols = get_stub_types_dict("stubs-handwritten")

    def test_lists_handwritten(self) -> None:
        assert "passlib.hash.bcrypt" in self.symbols

        assert "passlib.hash.bcrypt.using" in self.symbols
        assert "passlib.hash.bcrypt.identify" in self.symbols
        assert "passlib.hash.bcrypt.verify" in self.symbols
        assert "passlib.hash.bcrypt.encrypt" in self.symbols
        assert "passlib.hash.bcrypt.hash" in self.symbols

        assert "passlib.hash.md5_crypt" in self.symbols

        assert "freezegun.api.freeze_time" in self.symbols
        assert "freezegun.api.TickingDateTimeFactory.time_to_freeze"
        assert "freezegun.api.TickingDateTimeFactory.start"
        assert "freezegun.api.TickingDateTimeFactory.__init__"
        assert "freezegun.api.TickingDateTimeFactory.__call__"

    def test_method_stub(self) -> None:
        hash_method = cast(Decorator, self.symbols["passlib.hash.bcrypt.hash"])
        assert isinstance(hash_method, Decorator)
        assert hash_method.func.fullname() == "passlib.hash.bcrypt.hash"
        assert hash_method.func.arg_names == ["cls", "text"]
        assert hash_method.func.arguments[0].type_annotation is None

        text_param = cast(UnboundType, hash_method.func.arguments[1].type_annotation)
        assert isinstance(text_param, UnboundType)
        assert text_param.name == "str"

        assert isinstance(hash_method.func.type, CallableType)
        assert isinstance(hash_method.func.type.ret_type, Instance)
        assert hash_method.func.type.ret_type.type.name() == "str"

    def test_type_alias(self) -> None:
        type_alias = cast(TypeAlias, self.symbols["freezegun.api.FreezeTimeInputType"])
        assert isinstance(type_alias, TypeAlias)
        assert type_alias.name() == "FreezeTimeInputType"
        assert isinstance(type_alias.target, UnionType)

        assert str(type_alias.target.items[0]) == "builtins.str"
        assert str(type_alias.target.items[1]) == "datetime.date"
        assert isinstance(type_alias.target.items[3], CallableType)
        assert isinstance(type_alias.target.items[5], AnyType)

    def test_inherited(self) -> None:
        bcrypt = self.symbols.get("passlib.hash.bcrypt")
        assert bcrypt
        assert isinstance(bcrypt, TypeInfo)
        assert bcrypt.get_method("hash") is None
        assert {b.type.fullname() for b in bcrypt.bases} == {"builtins.object"}

        hash_method = bcrypt.get("hash")
        assert hash_method
        assert hash_method.fullname == "passlib.hash.bcrypt.hash"


class TestGetStubTypesWithGeneratedStubs:
    symbols: Dict[str, SymbolNode]

    @classmethod
    def setup_class(cls) -> None:
        cls.symbols = get_stub_types_dict("stubs-generated")

    def test_inherited(self) -> None:
        bcrypt = self.symbols.get("passlib.hash.bcrypt")
        assert isinstance(bcrypt, TypeInfo)

        # the hash method is not declared in the bcrypt class directly
        assert not bcrypt.names.get("hash")
        assert "passlib.hash.bcrypt.hash" not in self.symbols

        # but it can be resolved from definitions inherited from base classes
        hash_method = bcrypt.get("hash")
        assert hash_method and isinstance(hash_method.node, Decorator)


class TestStubAnalyzer:
    def test_main_returns_0(self) -> None:
        result = main()
        assert result == 0
