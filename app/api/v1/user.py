from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import (
    UserListItem,
    UserQuery,
    UserCreateResponse,
    UserCreate,
    UserUpdate,
)
from app.schemas.common import PageData, SuccessResponse
from app.services.user_service import (
    del_user_service,
    get_user_service,
    list_user_service,
    create_user_service,
    update_user_service,
)
from app.core.response import success, page_success

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/create", summary="创建用户", response_model=SuccessResponse[UserCreateResponse]
)
def create_user_api(user_in: UserCreate, db: Session = Depends(get_db)):
    user = create_user_service(db, user_in)
    return success(user)


@router.post(
    "/delete/{user_id}",
    summary="删除用户",
    response_model=SuccessResponse[UserListItem],
)
def del_user_api(user_id: int, db: Session = Depends(get_db)):
    user = del_user_service(db, user_id)
    return success(user)


@router.post(
    "/update", summary="更新用户", response_model=SuccessResponse[UserCreateResponse]
)
def create_user_api(user_in: UserUpdate, db: Session = Depends(get_db)):
    user = update_user_service(db, user_in)
    return success(user)


@router.post(
    "/getUserList",
    summary="获取用户列表",
    response_model=SuccessResponse[PageData[UserListItem]],
)
def list_user_api(user_in: UserQuery, db: Session = Depends(get_db)):
    rows, total = list_user_service(db, user_in)
    return page_success(rows, total)


@router.post(
    "/{user_id}", summary="获取用户详情", response_model=SuccessResponse[UserListItem]
)
def get_user_api(user_id: int, db: Session = Depends(get_db)):
    user = get_user_service(db, user_id)
    return success(user)
