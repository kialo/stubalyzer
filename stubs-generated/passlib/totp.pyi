# Stubs for passlib.totp (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from passlib.exc import InvalidTokenError as InvalidTokenError, MalformedTokenError as MalformedTokenError, TokenError as TokenError, UsedTokenError as UsedTokenError
from passlib.utils import SequenceMixin
from typing import Any, Optional

class AppWallet:
    salt_size: int = ...
    encrypt_cost: int = ...
    default_tag: Any = ...
    def __init__(self, secrets: Optional[Any] = ..., default_tag: Optional[Any] = ..., encrypt_cost: Optional[Any] = ..., secrets_path: Optional[Any] = ...) -> None: ...
    @property
    def has_secrets(self): ...
    def get_secret(self, tag: Any): ...
    def encrypt_key(self, key: Any): ...
    def decrypt_key(self, enckey: Any): ...

class TOTP:
    min_json_version: int = ...
    json_version: int = ...
    wallet: Any = ...
    now: Any = ...
    digits: int = ...
    alg: str = ...
    label: Any = ...
    issuer: Any = ...
    period: int = ...
    changed: bool = ...
    @classmethod
    def using(cls, digits: Optional[Any] = ..., alg: Optional[Any] = ..., period: Optional[Any] = ..., issuer: Optional[Any] = ..., wallet: Optional[Any] = ..., now: Optional[Any] = ..., **kwds: Any): ...
    @classmethod
    def new(cls, **kwds: Any): ...
    key: Any = ...
    encrypted_key: Any = ...
    def __init__(self, key: Optional[Any] = ..., format: str = ..., new: bool = ..., digits: Optional[Any] = ..., alg: Optional[Any] = ..., size: Optional[Any] = ..., period: Optional[Any] = ..., label: Optional[Any] = ..., issuer: Optional[Any] = ..., changed: bool = ..., **kwds: Any) -> None: ...
    @property
    def key(self): ...
    @key.setter
    def key(self, value: Any) -> None: ...
    @property
    def encrypted_key(self): ...
    @encrypted_key.setter
    def encrypted_key(self, value: Any) -> None: ...
    @property
    def hex_key(self): ...
    @property
    def base32_key(self): ...
    def pretty_key(self, format: str = ..., sep: str = ...): ...
    @classmethod
    def normalize_time(cls, time: Any): ...
    def normalize_token(self_or_cls: Any, token: Any): ...
    def generate(self, time: Optional[Any] = ...): ...
    @classmethod
    def verify(cls, token: Any, source: Any, **kwds: Any): ...
    def match(self, token: Any, time: Optional[Any] = ..., window: int = ..., skew: int = ..., last_counter: Optional[Any] = ...): ...
    @classmethod
    def from_source(cls, source: Any): ...
    @classmethod
    def from_uri(cls, uri: Any): ...
    def to_uri(self, label: Optional[Any] = ..., issuer: Optional[Any] = ...): ...
    @classmethod
    def from_json(cls, source: Any): ...
    def to_json(self, encrypt: Optional[Any] = ...): ...
    @classmethod
    def from_dict(cls, source: Any): ...
    def to_dict(self, encrypt: Optional[Any] = ...): ...

class TotpToken(SequenceMixin):
    totp: Any = ...
    token: Any = ...
    counter: Any = ...
    def __init__(self, totp: Any, token: Any, counter: Any) -> None: ...
    def start_time(self): ...
    def expire_time(self): ...
    @property
    def remaining(self): ...
    @property
    def valid(self): ...

class TotpMatch(SequenceMixin):
    totp: Any = ...
    counter: int = ...
    time: int = ...
    window: int = ...
    def __init__(self, totp: Any, counter: Any, time: Any, window: int = ...) -> None: ...
    def expected_counter(self): ...
    def skipped(self): ...
    def expire_time(self): ...
    def cache_seconds(self): ...
    def cache_time(self): ...
