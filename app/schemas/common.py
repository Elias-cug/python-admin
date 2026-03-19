from __future__ import annotations

from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class SuccessResponse(BaseSchema, Generic[T]):
    code: int = 0
    message: str = "success"
    data: T | None = None


class PageData(BaseSchema, Generic[T]):
    data: list[T] = Field(default_factory=list)
    total: int = 0


class PaginationSchema(BaseSchema):
    page: int = Field(1, ge=1, description="page number")
    page_size: int = Field(20, ge=1, le=200, description="page size")


class OrderSchema(BaseSchema):
    sort_by: str = Field("created_at", description="sort field")
    order: Literal["asc", "desc"] = Field("desc", description="sort order")


class ListQuerySchema(PaginationSchema, OrderSchema):
    pass
