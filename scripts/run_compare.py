import os
import sys
from pathlib import Path

from stub_analyzer.analyze import analyze_stubs

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / ".."


if __name__ == "__main__":
    success = analyze_stubs(
        f"{BASE_DIR}/mypy.ini",
        f"{BASE_DIR}/stubs-handwritten",
        f"{BASE_DIR}/stubs-generated",
    )
    sys.exit(0 if success else 1)
