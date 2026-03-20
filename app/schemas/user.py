from __future__ import annotations

from datetime import datetime

from pydantic import Field, ValidationInfo, field_serializer, field_validator

from app.core.exceptions import BusinessError

from .common import BaseSchema, ListQuerySchema


class UserCreate(BaseSchema):
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


class UserCreateResponse(BaseSchema):
    id: int | None = None
    tenant_id: int | None = None
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    status: int | None = None


class UserUpdate(BaseSchema):
    id: int
    tenant_id: int
    email: str | None = None
    phone: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    status: int | None = None


class UserQuery(ListQuerySchema):
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


class UserListItem(BaseSchema):
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
