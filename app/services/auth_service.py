from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BusinessError
from app.core.redis_client import get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.user import get_user_by_username, get_user

from app.schemas.auth import LoginIn, LoginOut, RefreshOut


def _now() -> datetime:
    return datetime.now()


def _refresh_key(jti: str) -> str:
    return f"auth:refresh:{jti}"


def login_service(db: Session, login_in: LoginIn, *, client_ip: str | None) -> LoginOut:
    settings = get_settings()

    user = get_user_by_username(db, login_in.tenant_id, login_in.username)
    if not user:
        raise BusinessError("账号或密码错误")

    if int(user.status) != 1:
        raise BusinessError("用户已禁用")

    now = _now()

    is_locked = bool(getattr(user, "is_locked", False) or False)
    locked_until = getattr(user, "locked_until", None)

    if is_locked:
        if locked_until is None or locked_until > now:
            raise BusinessError("账号已锁定，请5分钟后重试")
        # Lock expired; unlock
        user.is_locked = False
        user.locked_until = None
        user.login_failed_count = 0

    if not verify_password(login_in.password, user.password_hash):
        failed = int(getattr(user, "login_failed_count", 0) or 0) + 1
        user.login_failed_count = failed
        user.last_login_failed_at = now

        if failed >= settings.login_lock_threshold:
            user.is_locked = True
            user.locked_until = now + timedelta(minutes=settings.login_lock_minutes)

        db.commit()
        raise BusinessError("账号或密码错误")

    # success
    user.login_failed_count = 0
    user.last_login_failed_at = None
    user.is_locked = False
    user.locked_until = None
    user.last_login_at = now
    if client_ip:
        user.last_login_ip = client_ip
    db.commit()

    pwd_updated_at = getattr(user, "password_updated_at", None)
    access_token, expires_in, _access_jti = create_access_token(
        user_id=int(user.id),
        tenant_id=int(user.tenant_id),
        pwd_updated_at=pwd_updated_at,
    )
    refresh_token, refresh_ttl, refresh_jti = create_refresh_token(
        user_id=int(user.id),
        tenant_id=int(user.tenant_id),
        pwd_updated_at=pwd_updated_at,
    )

    r = get_redis()
    r.setex(_refresh_key(refresh_jti), refresh_ttl, str(user.id))

    must_change_password = bool(getattr(user, "is_first_login", False) or False) or (
        not bool(getattr(user, "is_password_changed", True) or False)
    )

    return LoginOut(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user_id=int(user.id),
        must_change_password=must_change_password,
    )


def refresh_service(db: Session, refresh_token: str) -> RefreshOut:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise BusinessError("refresh_token无效")

    user_id = int(payload.get("sub"))
    tenant_id = int(payload.get("tid"))
    jti = payload.get("jti")
    if not jti:
        raise BusinessError("refresh_token无效")

    r = get_redis()
    key = _refresh_key(jti)
    stored = r.get(key)
    if not stored or stored != str(user_id):
        raise BusinessError("refresh_token已失效，请重新登录")

    user = get_user(db, user_id)
    if not user or int(user.tenant_id) != tenant_id:
        raise BusinessError("refresh_token已失效，请重新登录")

    pwd_at = int(payload.get("pwd_at") or 0)
    pwd_updated_at = getattr(user, "password_updated_at", None)
    if pwd_updated_at and int(pwd_updated_at.timestamp()) > pwd_at:
        r.delete(key)
        raise BusinessError("refresh_token已失效，请重新登录")

    # rotation
    r.delete(key)
    new_access, expires_in, _ = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        pwd_updated_at=pwd_updated_at,
    )
    new_refresh, refresh_ttl, new_jti = create_refresh_token(
        user_id=user_id,
        tenant_id=tenant_id,
        pwd_updated_at=pwd_updated_at,
    )
    r.setex(_refresh_key(new_jti), refresh_ttl, str(user_id))

    return RefreshOut(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=expires_in,
    )


def logout_service(refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)
    except Exception:
        return

    if payload.get("type") != "refresh":
        return
    jti = payload.get("jti")
    if not jti:
        return

    r = get_redis()
    r.delete(_refresh_key(jti))

