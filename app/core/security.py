from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

# NOTE:
# - `bcrypt` has a 72-byte input limit and backend-compat issues across versions.
# - `pbkdf2_sha256` uses only stdlib primitives and avoids bcrypt backend quirks.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

DEFAULT_INITIAL_PASSWORD = "Admin@1234"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(*, user_id: int, tenant_id: int, pwd_updated_at: datetime | None) -> tuple[str, int, str]:
    settings = get_settings()
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured")

    jti = uuid.uuid4().hex
    expires_in = int(settings.access_token_exp_minutes * 60)
    now = _utcnow()

    payload = {
        "type": "access",
        "sub": str(user_id),
        "tid": int(tenant_id),
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
        "pwd_at": int(pwd_updated_at.timestamp()) if pwd_updated_at else 0,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_in, jti


def create_refresh_token(*, user_id: int, tenant_id: int, pwd_updated_at: datetime | None) -> tuple[str, int, str]:
    settings = get_settings()
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured")

    jti = uuid.uuid4().hex
    ttl_seconds = int(settings.refresh_token_exp_days * 24 * 60 * 60)
    now = _utcnow()

    payload = {
        "type": "refresh",
        "sub": str(user_id),
        "tid": int(tenant_id),
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "pwd_at": int(pwd_updated_at.timestamp()) if pwd_updated_at else 0,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, ttl_seconds, jti


def decode_token(token: str) -> dict:
    settings = get_settings()
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured")
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise ValueError("invalid token") from e
