from typing import Generic, TypeVar, Optional, List

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    code: int = Field(default=0, description="Status Code")
    data: Optional[T] = Field(default=None, description="Response data")
    message: str = Field(default="ok", description="Response message")

    @classmethod
    def success(cls, data: Optional[T] = None, message: str = "ok") -> "BaseResponse[T]":
        return cls(code=0, data=data, message=message)

    @classmethod
    def error(cls, code: int, message: str) -> "BaseResponse[T]":
        return cls(code=code, data=None, message=message)


class PageRequest(BaseModel):
    current: int = Field(default=1, ge=1, description="Current Page")
    page_size: int = Field(default=10, ge=1, le=100, alias="pageSize", description="Page Size")
    sort_field: Optional[str] = Field(default=None, alias="sortField", description="Sort Field")
    sort_order: Optional[str] = Field(default="descend", alias="sortOrder", description="Sort Order")


class DeleteRequest(BaseModel):
    id: int = Field(..., description="Delete Id")


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., min_length=1, description="ID 列表")


class IdRequest(BaseModel):
    id: int = Field(..., description="ID")


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""
    records: List[T]
    total: int
    current: int
    page_size: int = Field(..., alias="pageSize")

    class Config:
        populate_by_name = True

    @classmethod
    def of(cls, records: List[T], total: int, current: int, page_size: int) -> "PageResponse[T]":
        return cls(records=records, total=total, current=current, page_size=page_size)
