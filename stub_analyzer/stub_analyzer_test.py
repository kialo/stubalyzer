from os.path import abspath, dirname
from pathlib import Path
from typing import Dict, cast
from unittest.mock import Mock

from mypy.build import State
from mypy.nodes import Decorator, FuncDef, SymbolNode, TypeInfo
from mypy.types import UnboundType

from stub_analyzer.api import get_stub_types, should_include_module

from .stub_analyzer import main


def module(path: str) -> State:
    return Mock(State, path=path)


class TestShouldIncludeModule:
    def test_excludes_external(self) -> None:
        assert not should_include_module(module("path/to/typeshed/module.pyi"))
        assert not should_include_module(module("site-packages/mypy/some.pyi"))
        assert not should_include_module(module("path/to/builtins.pyi"))
        assert should_include_module(module("some/other/module.pyi"))
        assert should_include_module(module("stubs-handwritten/passlib/__init__.pyi"))


class TestGetStubTypes:
    symbols: Dict[str, SymbolNode]

    @classmethod
    def setup_class(cls) -> None:
        package_path = Path(dirname(abspath(__file__))).parent
        stubs_path = (package_path / "stubs-handwritten").absolute()
        conf_path = (package_path / "mypy.ini").absolute()

        assert stubs_path.exists()
        assert conf_path.exists()

        cls.symbols = {
            s.fullname(): s for s in get_stub_types(str(stubs_path), str(conf_path))
        }

    def test_lists_handwritten(self) -> None:
        assert "passlib.hash.bcrypt" in self.symbols

        hash_method = cast(Decorator, self.symbols["passlib.hash.bcrypt.hash"])
        assert isinstance(hash_method, Decorator)
        assert hash_method.func.fullname() == "passlib.hash.bcrypt.hash"
        assert hash_method.func.arg_names == ["cls", "text"]
        assert hash_method.func.arguments[0].type_annotation is None

        text_param = cast(UnboundType, hash_method.func.arguments[1].type_annotation)
        assert isinstance(text_param, UnboundType)
        assert text_param.name == "str"

    def test_inherited(self) -> None:
        bcrypt = self.symbols.get("passlib.hash.bcrypt")
        assert bcrypt
        assert isinstance(bcrypt, TypeInfo)
        assert bcrypt.get_method("hash") is None
        assert {b.type.fullname() for b in bcrypt.bases} == {"builtins.object"}

        hash_method = bcrypt.get("hash")
        assert hash_method
        assert hash_method.fullname == "passlib.hash.bcrypt.hash"


class TestStubAnalyzer:
    def test_main_returns_0(self) -> None:
        result = main()
        assert result == 0
