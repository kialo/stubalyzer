# Stubs for passlib.tests.test_crypto_digest (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from passlib.tests.utils import TestCase
from typing import Any

class HashInfoTest(TestCase):
    descriptionPrefix: str = ...
    norm_hash_formats: Any = ...
    norm_hash_samples: Any = ...
    def test_norm_hash_name(self) -> None: ...
    def test_lookup_hash_ctor(self) -> None: ...
    def test_lookup_hash_metadata(self) -> None: ...
    def test_lookup_hash_alt_types(self) -> None: ...

class Pbkdf1_Test(TestCase):
    descriptionPrefix: str = ...
    pbkdf1_tests: Any = ...
    def test_known(self) -> None: ...
    def test_border(self): ...

class Pbkdf2Test(TestCase):
    descriptionPrefix: Any = ...
    pbkdf2_test_vectors: Any = ...
    def test_known(self) -> None: ...
    def test_backends(self) -> None: ...
    def test_border(self): ...
    def test_default_keylen(self): ...
