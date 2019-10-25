import os
import sys
from pathlib import Path
from typing import Dict, Iterable

from mypy.nodes import SymbolNode
from stub_analyzer import get_stub_types, lookup_symbol

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".."
MYPY_CONF = BASE_DIR / "mypy.ini"


def find_missing_symbols() -> Iterable[str]:
    stub_types_base = get_stub_types(
        str(BASE_DIR / "stubs-handwritten"), str(MYPY_CONF)
    )
    stub_types_reference = get_stub_types(
        str(BASE_DIR / "stubs-generated"), str(MYPY_CONF)
    )

    generated_map: Dict[str, SymbolNode] = {
        sym.fullname(): sym for sym in stub_types_reference
    }

    for symbol in stub_types_base:
        lookup_result = lookup_symbol(generated_map, symbol)
        generated_symbol = lookup_result.symbol
        if not generated_symbol:
            yield f"Could not resolve symbol <{symbol.fullname()}> in generated stubs."
        else:
            if generated_symbol.fullname() != symbol.fullname():
                yield (
                    f"Found symbol <{symbol.fullname()}> in different location"
                    f" <{generated_symbol.fullname()}>"
                )


if __name__ == "__main__":
    result = list(find_missing_symbols())
    print("\n".join(result))

    sys.exit(1 if result else 0)
