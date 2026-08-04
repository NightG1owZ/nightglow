from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class TagAddRequest(BaseModel):
    """新增标签请求"""
    name: str = Field(..., max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")


class TagUpdateRequest(BaseModel):
    """更新标签请求"""
    id: int = Field(..., description="标签 ID")
    name: Optional[str] = Field(None, max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")


class TagQueryRequest(PageRequest):
    """标签分页查询请求"""
    name: Optional[str] = Field(None, description="标签名称")


class TagVO(BaseModel):
    """标签视图对象"""
    id: int
    name: str
    color: Optional[str] = None
    article_count: int
    create_time: datetime = Field(..., alias="createTime")
    update_time: datetime = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True
