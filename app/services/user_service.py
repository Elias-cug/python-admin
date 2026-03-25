from __future__ import annotations


from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError
from app.core.security import (
    DEFAULT_INITIAL_PASSWORD,
    hash_password,
    verify_password,
)
from app.crud.user import (
    create_user,
    del_user,
    get_user,
    list_user,
    update_user,
    update_user_password,
)
from app.schemas.user import (
    UserChangePassword,
    UserCreate,
    UserQuery,
    UserResetPassword,
    UserUpdate,
)


def create_user_service(db: Session, user_in: UserCreate, *, operator_id: int | None = None):
    password_hash = hash_password(DEFAULT_INITIAL_PASSWORD)
    user = create_user(
        db,
        user_in,
        password_hash=password_hash,
        created_by=operator_id,
        updated_by=operator_id,
    )
    return user


def change_password_service(
    db: Session, change_in: UserChangePassword, *, operator_id: int | None = None
):
    user = get_user(db, change_in.user_id)
    if not user:
        raise BusinessError("用户不存在")

    if not verify_password(change_in.old_password, user.password_hash):
        raise BusinessError("旧密码不正确")

    if verify_password(change_in.new_password, user.password_hash):
        raise BusinessError("新密码不能与旧密码相同")

    new_hash = hash_password(change_in.new_password)
    updated = update_user_password(
        db,
        change_in.user_id,
        password_hash=new_hash,
        updated_by=operator_id,
        password_updated_at=datetime.now(),
        is_password_changed=True,
        is_first_login=False,
        login_failed_count=0,
        last_login_failed_at=None,
        is_locked=False,
        locked_until=None,
    )
    return updated


def reset_password_service(
    db: Session, reset_in: UserResetPassword, *, operator_id: int | None = None
):
    user = get_user(db, reset_in.user_id)
    if not user:
        raise BusinessError("用户不存在")

    new_hash = hash_password(DEFAULT_INITIAL_PASSWORD)
    updated = update_user_password(
        db,
        reset_in.user_id,
        password_hash=new_hash,
        updated_by=operator_id,
        password_updated_at=datetime.now(),
        is_password_changed=False,
        is_first_login=True,
        login_failed_count=0,
        last_login_failed_at=None,
        is_locked=False,
        locked_until=None,
    )
    return updated


def del_user_service(db: Session, user_id: int, *, operator_id: int | None = None):
    user = del_user(db, user_id, updated_by=operator_id)
    return user

def update_user_service(db: Session, user_in: UserUpdate, *, operator_id: int | None = None):
    user = update_user(db, user_in, updated_by=operator_id)
    return user

def get_user_service(db: Session, user_id: int):
    user = get_user(db, user_id)
    return user

def list_user_service(db: Session, user_in: UserQuery):
    users, total = list_user(db, user_in)
    return users, total
