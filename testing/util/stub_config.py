import os
from pathlib import Path


class WithStubTestConfig:
    _base_dir: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
    _handwritten_stubs_path: Path = _base_dir / "stubs-handwritten"
    _generated_stubs_path: Path = _base_dir / "stubs-generated"
    _mypy_conf_path: Path = _base_dir / "mypy.ini"

    def get_expectations_path(self, file: str) -> str:
        return str(self._base_dir / "stub-expectations" / file)

    @property
    def base_dir(self) -> str:
        return str(self._base_dir)

    @property
    def handwritten_stubs_path(self) -> str:
        return str(self._handwritten_stubs_path)

    @property
    def generated_stubs_path(self) -> str:
        return str(self._generated_stubs_path)

    @property
    def mypy_config_path(self) -> str:
        return str(self._mypy_conf_path)
