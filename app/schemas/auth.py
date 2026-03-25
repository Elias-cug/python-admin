from __future__ import annotations

from pydantic import Field

from .common import BaseSchema


class LoginIn(BaseSchema):
    tenant_id: int = Field(..., description="tenant id")
    username: str = Field(..., min_length=1, description="username")
    password: str = Field(..., min_length=1, description="password")


class TokenPair(BaseSchema):
    access_token: str
    refresh_token: str
    expires_in: int = Field(..., description="access token ttl (seconds)")


class LoginOut(TokenPair):
    user_id: int
    must_change_password: bool = False


class RefreshIn(BaseSchema):
    refresh_token: str = Field(..., min_length=1)


class RefreshOut(TokenPair):
    pass


class LogoutIn(BaseSchema):
    refresh_token: str = Field(..., min_length=1)

