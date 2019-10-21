from os.path import abspath, dirname
from pathlib import Path
from typing import Dict, cast

from mypy.nodes import Decorator, SymbolNode, TypeAlias, TypeInfo
from mypy.types import AnyType, CallableType, Instance, UnboundType, UnionType

from stub_analyzer.api import get_stub_types


def get_stub_types_dict(stub_folder: str) -> Dict[str, SymbolNode]:
    package_path = Path(dirname(abspath(__file__))).parent
    stubs_path = (package_path / stub_folder).absolute()
    conf_path = (package_path / "mypy.ini").absolute()

    assert stubs_path.exists()
    assert conf_path.exists()

    return {s.fullname(): s for s in get_stub_types(str(stubs_path), str(conf_path))}


class TestGetStubTypesWithHandwrittenStubs:
    symbols: Dict[str, SymbolNode]

    @classmethod
    def setup_class(cls) -> None:
        cls.symbols = get_stub_types_dict("stubs-handwritten")

    def test_lists_handwritten(self) -> None:
        """ Ensures that the expected hand-written stubs are there; non-exhaustive """
        assert "passlib.hash.bcrypt" in self.symbols
        assert "passlib.hash.bcrypt.using" in self.symbols
        assert "passlib.hash.bcrypt.identify" in self.symbols
        assert "passlib.hash.bcrypt.verify" in self.symbols
        assert "passlib.hash.bcrypt.encrypt" in self.symbols
        assert "passlib.hash.bcrypt.hash" in self.symbols

        assert "passlib.hash.md5_crypt" in self.symbols
        assert "passlib.hash.md5_crypt.using" in self.symbols
        assert "passlib.hash.md5_crypt.identify" in self.symbols
        assert "passlib.hash.md5_crypt.verify" in self.symbols
        assert "passlib.hash.md5_crypt.encrypt" in self.symbols
        assert "passlib.hash.md5_crypt.hash" in self.symbols

        assert "freezegun.api.FreezeTimeInputType" in self.symbols
        assert "freezegun.api.freeze_time" in self.symbols
        assert "freezegun.api.TickingDateTimeFactory.time_to_freeze"
        assert "freezegun.api.TickingDateTimeFactory.start"
        assert "freezegun.api.TickingDateTimeFactory.__init__"
        assert "freezegun.api.TickingDateTimeFactory.__call__"
        assert "freezegun.api.CallableT"

    def test_method_stub(self) -> None:
        hash_method = cast(Decorator, self.symbols["passlib.hash.bcrypt.hash"])
        assert isinstance(hash_method, Decorator)
        assert hash_method.func.fullname() == "passlib.hash.bcrypt.hash"

        # function arguments
        assert hash_method.func.arg_names == ["cls", "text"]
        assert hash_method.func.arguments[0].type_annotation is None

        text_param = cast(UnboundType, hash_method.func.arguments[1].type_annotation)
        assert isinstance(text_param, UnboundType)
        assert text_param.name == "str"

        # function return value
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
        assert str(type_alias.target.items[2]) == "datetime.timedelta"
        assert isinstance(type_alias.target.items[3], CallableType)
        assert str(type_alias.target.items[4]) == "types.GeneratorType"
        assert isinstance(type_alias.target.items[5], AnyType)

    def test_inheritance(self) -> None:
        bcrypt = self.symbols.get("passlib.hash.bcrypt")
        assert bcrypt
        assert isinstance(bcrypt, TypeInfo)
        assert {b.type.fullname() for b in bcrypt.bases} == {"builtins.object"}


class TestGetStubTypesWithGeneratedStubs:
    symbols: Dict[str, SymbolNode]

    @classmethod
    def setup_class(cls) -> None:
        cls.symbols = get_stub_types_dict("stubs-generated")

    def test_lists_generated_stubs(self) -> None:
        """ Checks if the expected stubs are there; non-exhaustive """
        assert "freezegun.api.FakeDate" in self.symbols
        assert "passlib.hash.bcrypt" in self.symbols
        assert "passlib.hash.bcrypt.backends" in self.symbols
        assert "passlib.hash.md5_crypt" in self.symbols
        assert "passlib.ifc.PasswordHash.truncate_size" in self.symbols
        assert "freezegun.api.call_stack_inspection_limit" in self.symbols

        # the following members are not listed because their definitions are defined in a base class
        assert "passlib.hash.bcrypt.using" not in self.symbols
        assert "passlib.hash.bcrypt.identify" not in self.symbols
        assert "passlib.hash.bcrypt.verify" not in self.symbols
        assert "passlib.hash.bcrypt.encrypt" not in self.symbols
        assert "passlib.hash.bcrypt.hash" not in self.symbols

        # some things that are not part of the automatically generated stubs
        assert "freezegun.api.FreezeTimeInputType" not in self.symbols
        assert "freezegun.api.FactoryType" not in self.symbols

    def test_inherited_definitions(self) -> None:
        bcrypt = self.symbols.get("passlib.hash.bcrypt")
        assert isinstance(bcrypt, TypeInfo)

        # the hash method is not declared in the bcrypt class directly
        assert not bcrypt.names.get("hash")
        assert "passlib.hash.bcrypt.hash" not in self.symbols

        # but it can be resolved from definitions inherited from base classes
        hash_method = bcrypt.get("hash")
        assert hash_method and isinstance(hash_method.node, Decorator)

    def test_base_classes(self) -> None:
        FakeDatetimeMeta = self.symbols.get("freezegun.api.FakeDatetimeMeta")
        assert isinstance(FakeDatetimeMeta, TypeInfo)
        assert {b.type.fullname() for b in FakeDatetimeMeta.bases} == {
            "freezegun.api.FakeDateMeta"
        }

        FakeDateMeta = self.symbols.get("freezegun.api.FakeDateMeta")
        assert isinstance(FakeDateMeta, TypeInfo)
        assert {b.type.fullname() for b in FakeDateMeta.bases} == {"builtins.type"}
