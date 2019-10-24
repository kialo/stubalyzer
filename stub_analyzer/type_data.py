import json
import os
from pathlib import Path
from typing import Any, Dict, Tuple, cast

from mypy.nodes import SymbolNode

from .types import RelevantSymbolNode

TEST_DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "test_data"
SYMBOL_DATA_DIR = TEST_DATA_DIR / "symbols"
REFERENCE_DATA_DIR = TEST_DATA_DIR / "reference_symbols"


class TypeData:
    symbols: Dict[str, RelevantSymbolNode] = {}
    reference_symbols: Dict[str, RelevantSymbolNode] = {}

    def __init__(self) -> None:
        for f in os.listdir(str(SYMBOL_DATA_DIR)):
            if f.endswith(".json"):
                with open(str(SYMBOL_DATA_DIR / f)) as handle:
                    data = json.load(handle)

                symbol = self.deserialize_node(data)
                self.symbols[symbol.fullname()] = symbol

        for f in os.listdir(str(REFERENCE_DATA_DIR)):
            if f.endswith(".json"):
                with open(str(REFERENCE_DATA_DIR / f)) as handle:
                    data = json.load(handle)

                symbol = self.deserialize_node(data)
                self.reference_symbols[symbol.fullname()] = symbol

    def deserialize_node(self, data: Dict[str, Any]) -> RelevantSymbolNode:
        return cast(RelevantSymbolNode, SymbolNode.deserialize(data))

    def get_symbol_and_reference(
        self, fullname: str
    ) -> Tuple[RelevantSymbolNode, RelevantSymbolNode]:
        return self.get_symbol(fullname), self.get_reference_symbol(fullname)

    def get_symbol(self, fullname: str) -> RelevantSymbolNode:
        return self.symbols[fullname]

    def get_reference_symbol(self, fullname: str) -> RelevantSymbolNode:
        return self.reference_symbols[fullname]
