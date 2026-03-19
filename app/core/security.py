from __future__ import annotations

from passlib.context import CryptContext


# NOTE:
# - `bcrypt` has a 72-byte input limit and backend-compat issues across versions.
# - `pbkdf2_sha256` uses only stdlib primitives and avoids bcrypt backend quirks.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

DEFAULT_INITIAL_PASSWORD = "Admin@1234"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
