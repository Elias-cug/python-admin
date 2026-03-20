from __future__ import annotations


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


def create_user_service(db: Session, user_in: UserCreate):
    password_hash = hash_password(DEFAULT_INITIAL_PASSWORD)
    user = create_user(db, user_in, password_hash=password_hash)
    return user


def change_password_service(db: Session, change_in: UserChangePassword):
    user = get_user(db, change_in.user_id)
    if not user:
        raise BusinessError("用户不存在")

    if not verify_password(change_in.old_password, user.password_hash):
        raise BusinessError("旧密码不正确")

    if verify_password(change_in.new_password, user.password_hash):
        raise BusinessError("新密码不能与旧密码相同")

    new_hash = hash_password(change_in.new_password)
    updated = update_user_password(db, change_in.user_id, password_hash=new_hash)
    return updated


def reset_password_service(db: Session, reset_in: UserResetPassword):
    user = get_user(db, reset_in.user_id)
    if not user:
        raise BusinessError("用户不存在")

    new_hash = hash_password(DEFAULT_INITIAL_PASSWORD)
    updated = update_user_password(db, reset_in.user_id, password_hash=new_hash)
    return updated


def del_user_service(db: Session, user_id: int):
    user = del_user(db, user_id)
    return user

def update_user_service(db: Session, user_in: UserUpdate):
    user = update_user(db, user_in)
    return user

def get_user_service(db: Session, user_id: int):
    user = get_user(db, user_id)
    return user

def list_user_service(db: Session, user_in: UserQuery):
    users, total = list_user(db, user_in)
    return users, total
