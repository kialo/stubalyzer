# Stubs for passlib.handlers.postgres (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import passlib.utils.handlers as uh
from typing import Any

class postgres_md5(uh.HasUserContext, uh.StaticHandler):
    name: str = ...
    checksum_chars: Any = ...
    checksum_size: int = ...
