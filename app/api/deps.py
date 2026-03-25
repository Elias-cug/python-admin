from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.exceptions import BusinessError
from app.core.security import decode_token
from app.crud.user import get_user


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None, alias="Authorization"),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise BusinessError("未登录", code=401)

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise BusinessError("未登录", code=401)

    try:
        payload = decode_token(token)
    except ValueError:
        raise BusinessError("无效token", code=401)

    if payload.get("type") != "access":
        raise BusinessError("无效token", code=401)

    try:
        user_id = int(payload.get("sub") or 0)
        tenant_id = int(payload.get("tid") or 0)
    except (TypeError, ValueError):
        raise BusinessError("无效token", code=401)

    if not user_id or not tenant_id:
        raise BusinessError("无效token", code=401)

    user = get_user(db, user_id)
    if not user or int(user.tenant_id) != tenant_id:
        raise BusinessError("未登录", code=401)

    if int(user.status) != 1:
        raise BusinessError("用户已禁用", code=403)

    pwd_at = int(payload.get("pwd_at") or 0)
    pwd_updated_at = getattr(user, "password_updated_at", None)
    if pwd_updated_at and int(pwd_updated_at.timestamp()) > pwd_at:
        raise BusinessError("token已失效，请重新登录", code=401)

    return user
