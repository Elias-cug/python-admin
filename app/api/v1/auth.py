from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.response import success
from app.schemas.auth import LoginIn, LoginOut, LogoutIn, RefreshIn, RefreshOut
from app.schemas.common import SuccessResponse
from app.schemas.user import UserOut
from app.services.auth_service import (
    login_service,
    logout_strong_service,
    refresh_service,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", summary="登录", response_model=SuccessResponse[LoginOut])
def login_api(login_in: LoginIn, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else None
    out = login_service(db, login_in, client_ip=client_ip)
    return success(out)


@router.post(
    "/refresh", summary="刷新token", response_model=SuccessResponse[RefreshOut]
)
def refresh_api(refresh_in: RefreshIn, db: Session = Depends(get_db)):
    out = refresh_service(db, refresh_in.refresh_token)
    return success(out)


@router.post("/logout", summary="退出登录", response_model=SuccessResponse[dict])
def logout_api(
    logout_in: LogoutIn,
    authorization: str | None = Header(None, alias="Authorization"),
):
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.split(" ", 1)[1].strip() or None
    logout_strong_service(
        refresh_token=logout_in.refresh_token, access_token=access_token
    )
    return success(message="退出成功")


@router.get("/me", summary="当前用户", response_model=SuccessResponse[UserOut])
def me_api(current_user=Depends(get_current_user)):
    return success(current_user)
