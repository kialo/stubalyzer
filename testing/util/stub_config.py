import os
from pathlib import Path


class WithStubTestConfig:
    _base_dir: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
    _handwritten_stubs_path: Path = _base_dir / "stubs-handwritten"
    _generated_stubs_path: Path = _base_dir / "stubs-generated"
    _mypy_config_path: Path = _base_dir / "mypy.ini"
    _expectations_dir_path = _base_dir / "stub-expectations"

    def get_expectations_path(self, file: str) -> str:
        return str(self._expectations_dir_path / file)

    @classmethod
    def get_base_dir(cls) -> str:
        return str(cls._base_dir)

    @classmethod
    def get_handwritten_stubs_path(cls) -> str:
        return str(cls._handwritten_stubs_path)

    @classmethod
    def get_generated_stubs_path(cls) -> str:
        return str(cls._generated_stubs_path)

    @classmethod
    def get_mypy_config_path(cls) -> str:
        return str(cls._mypy_config_path)

    def get_test_stub_path(self, dir: str) -> str:
        return str(self._base_dir / "test-stubs" / dir)

    @property
    def base_dir(self) -> str:
        return self.get_base_dir()

    @property
    def handwritten_stubs_path(self) -> str:
        return self.get_handwritten_stubs_path()

    @property
    def generated_stubs_path(self) -> str:
        return self.get_generated_stubs_path()

    @property
    def mypy_config_path(self) -> str:
        return self.get_mypy_config_path()
