# Stubs for passlib.tests.test_ext_django (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from django.contrib.auth.models import User
from passlib.tests.utils import TestCase
from typing import Any, Optional

class FakeUser(User):
    class Meta:
        app_label: Any = ...
    def saved_passwords(self): ...
    def pop_saved_passwords(self): ...
    def save(self, update_fields: Optional[Any] = ...) -> None: ...

class _ExtensionSupport:
    def assert_unpatched(self) -> None: ...
    def assert_patched(self, context: Optional[Any] = ...) -> None: ...
    def load_extension(self, check: bool = ..., **kwds: Any) -> None: ...
    def unload_extension(self) -> None: ...

class _ExtensionTest(TestCase, _ExtensionSupport):
    def setUp(self) -> None: ...

class DjangoBehaviorTest(_ExtensionTest):
    descriptionPrefix: str = ...
    patched: bool = ...
    config: Any = ...
    @property
    def context(self): ...
    def assert_unusable_password(self, user: Any) -> None: ...
    def assert_valid_password(self, user: Any, hash: Any = ..., saved: Optional[Any] = ...) -> None: ...
    def test_config(self) -> None: ...

class ExtensionBehaviorTest(DjangoBehaviorTest):
    descriptionPrefix: str = ...
    patched: bool = ...
    config: Any = ...
    def setUp(self) -> None: ...

class DjangoExtensionTest(_ExtensionTest):
    descriptionPrefix: str = ...
    def test_00_patch_control(self) -> None: ...
    def test_01_overwrite_detection(self) -> None: ...
    def test_02_handler_wrapper(self) -> None: ...
    def test_11_config_disabled(self) -> None: ...
    def test_12_config_presets(self) -> None: ...
    def test_13_config_defaults(self) -> None: ...
    def test_14_config_invalid(self) -> None: ...
    def test_21_category_setting(self): ...
