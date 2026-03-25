from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import (
    UserOut,
    UserQueryIn,
    UserCreateOut,
    UserCreateIn,
    UserUpdateIn,
    UserChangePasswordIn,
    UserResetPasswordIn,
)
from app.schemas.common import PageData, SuccessResponse
from app.services.user_service import (
    del_user_service,
    get_user_service,
    list_user_service,
    create_user_service,
    update_user_service,
    change_password_service,
    reset_password_service,
)
from app.core.response import success, page_success

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/create", summary="创建用户", response_model=SuccessResponse[UserCreateOut]
)
def create_user_api(
    user_in: UserCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = create_user_service(db, user_in, operator_id=int(current_user.id))
    return success(user)


@router.post(
    "/delete/{user_id}",
    summary="删除用户",
    response_model=SuccessResponse[UserOut],
)
def del_user_api(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = del_user_service(db, user_id, operator_id=int(current_user.id))
    return success(user)


@router.post(
    "/update", summary="更新用户", response_model=SuccessResponse[UserCreateOut]
)
def update_user_api(
    user_in: UserUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = update_user_service(db, user_in, operator_id=int(current_user.id))
    return success(user)


@router.post(
    "/getUserList",
    summary="获取用户列表",
    response_model=SuccessResponse[PageData[UserOut]],
)
def list_user_api(
    user_in: UserQueryIn,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    rows, total = list_user_service(db, user_in)
    return page_success(rows, total)


@router.post(
    "/changePassword",
    summary="修改密码",
    response_model=SuccessResponse[dict],
)
def change_password_api(
    change_in: UserChangePasswordIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_password_service(db, change_in, operator_id=int(current_user.id))
    return success(message="密码修改成功")


@router.post(
    "/resetPassword",
    summary="重置密码",
    response_model=SuccessResponse[dict],
)
def reset_password_api(
    reset_in: UserResetPasswordIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reset_password_service(db, reset_in, operator_id=int(current_user.id))
    return success(message="密码重置成功")


@router.post(
    "/{user_id}", summary="获取用户详情", response_model=SuccessResponse[UserOut]
)
def get_user_api(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    user = get_user_service(db, user_id)
    return success(user)
