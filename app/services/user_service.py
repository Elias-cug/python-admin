from __future__ import annotations


from sqlalchemy.orm import Session

from app.crud.user import create_user, del_user, get_user, list_user, update_user
from app.schemas.user import UserCreate, UserQuery, UserUpdate


def create_user_service(db: Session, user_in: UserCreate):
    user = create_user(db, user_in)
    return user

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

