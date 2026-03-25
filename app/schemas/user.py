from __future__ import annotations

from datetime import datetime

from pydantic import Field, ValidationInfo, field_serializer, field_validator

from app.core.exceptions import BusinessError

from .common import BaseSchema, ListQuerySchema


class UserCreateIn(BaseSchema):
    tenant_id: int
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    status: int | None = None

    @field_validator("email", mode="before")
    @classmethod
    def _emial_validate(cls, v):
        if isinstance(v, str) and not "@" in v:
            raise BusinessError("emial格式不对")
        return v


class UserCreateOut(BaseSchema):
    id: int | None = None
    tenant_id: int | None = None
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    status: int | None = None


class UserUpdateIn(BaseSchema):
    id: int
    tenant_id: int
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    status: int | None = None


class UserQueryIn(ListQuerySchema):
    tenant_id: int | None = None
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None

    @field_validator("username", "email", "phone", "display_name", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("created_from", "created_to", mode="before")
    @classmethod
    def _parse_datetime(cls, v, info: ValidationInfo):
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return None
            if "T" not in s and " " in s:
                s = s.replace(" ", "T", 1)
            if len(s) == 10 and s[4] == "-" and s[7] == "-":
                s = s + (
                    "T23:59:59" if info.field_name == "created_to" else "T00:00:00"
                )
            return datetime.fromisoformat(s)
        return v


class UserOut(BaseSchema):
    id: int
    tenant_id: int
    username: str
    email: str | None = None
    phone: str | None = None
    status: int
    display_name: str | None = None
    avatar_url: str | None = None
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("last_login_at", "created_at", "updated_at", when_used="json")
    def _serialize_dt(self, v: datetime | None):
        if v is None:
            return None
        return v.strftime("%Y-%m-%d %H:%M:%S")


class UserChangePasswordIn(BaseSchema):
    user_id: int = Field(..., description="user id")
    old_password: str = Field(..., min_length=1, description="old password")
    new_password: str = Field(..., min_length=8, description="new password")

    @field_validator("new_password")
    @classmethod
    def _new_password_not_empty(cls, v: str):
        if not v.strip():
            raise BusinessError("新密码不能为空")
        return v


class UserResetPasswordIn(BaseSchema):
    user_id: int = Field(..., description="user id")
    # Reset always uses DEFAULT_INITIAL_PASSWORD; no custom password accepted.
