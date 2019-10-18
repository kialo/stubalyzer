from typing import Any

from passlib.hash import bcrypt


def bcrypt_hash(text: str) -> Any:
    # reveal_type(bcrypt)
    # reveal_type(bcrypt.using)
    # reveal_type(bcrypt.using(rounds=10))
    # reveal_type(bcrypt.using(rounds=10).hash)
    # reveal_type(bcrypt.using(rounds=10).hash(text))
    return bcrypt.using(rounds=10).hash(text)


def md5_hash(text: str) -> Any:
    # reveal_type(bcrypt)
    # reveal_type(bcrypt.using)
    # reveal_type(bcrypt.using(rounds=10))
    # reveal_type(bcrypt.using(rounds=10).hash)
    # reveal_type(bcrypt.using(rounds=10).hash(text))
    return bcrypt.using(rounds=10).hash(text)