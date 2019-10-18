# Stubs for passlib.handlers.ldap_digests (Python 3.6)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any

from passlib.handlers.misc import plaintext
from passlib.utils import handlers as uh

class _Base64DigestHelper(uh.StaticHandler):
    ident = ...  # type: Any
    checksum_chars = ...  # type: Any

class _SaltedBase64DigestHelper(uh.HasRawSalt, uh.HasRawChecksum, uh.GenericHandler):
    setting_kwds = ...  # type: Any
    checksum_chars = ...  # type: Any
    ident = ...  # type: Any
    min_salt_size = ...  # type: int
    max_salt_size = ...  # type: int
    def to_string(self) -> Any: ...

class ldap_md5(_Base64DigestHelper):
    name = ...  # type: str
    ident = ...  # type: Any

class ldap_sha1(_Base64DigestHelper):
    name = ...  # type: str
    ident = ...  # type: Any

class ldap_salted_md5(_SaltedBase64DigestHelper):
    name = ...  # type: str
    ident = ...  # type: Any
    checksum_size = ...  # type: int

class ldap_salted_sha1(_SaltedBase64DigestHelper):
    name = ...  # type: str
    ident = ...  # type: Any
    checksum_size = ...  # type: int

class ldap_plaintext(plaintext):
    name = ...  # type: str
    @classmethod
    def identify(cls, hash: Any) -> Any: ...

# Names in __all__ with no definition:
#   ldap_bsdi_crypt
#   ldap_des_crypt
#   ldap_md5_crypt
#   ldap_sha1_cryptldap_bcrypt
#   ldap_sha256_crypt
#   ldap_sha512_crypt
