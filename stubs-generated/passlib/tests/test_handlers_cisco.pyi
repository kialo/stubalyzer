# Stubs for passlib.tests.test_handlers_cisco (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from .utils import HandlerCase, UserHandlerMixin
from typing import Any

class _PixAsaSharedTest(UserHandlerMixin, HandlerCase):
    requires_user: bool = ...
    pix_asa_shared_hashes: Any = ...
    def test_calc_digest_spoiler(self): ...

class cisco_pix_test(_PixAsaSharedTest):
    handler: Any = ...
    known_correct_hashes: Any = ...

class cisco_asa_test(_PixAsaSharedTest):
    handler: Any = ...
    known_correct_hashes: Any = ...

class cisco_type7_test(HandlerCase):
    handler: Any = ...
    salt_bits: int = ...
    salt_type: Any = ...
    known_correct_hashes: Any = ...
    known_unidentified_hashes: Any = ...
    def test_90_decode(self) -> None: ...
    def test_91_salt(self) -> None: ...
