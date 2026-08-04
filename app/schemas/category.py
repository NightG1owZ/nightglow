from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class CategoryAddRequest(BaseModel):
    """新增分类请求"""
    name: str = Field(..., max_length=50, description="分类名称")
    description: Optional[str] = Field(None, max_length=255, description="分类描述")
    sort: int = Field(default=0, description="排序")


class CategoryUpdateRequest(BaseModel):
    """更新分类请求"""
    id: int = Field(..., description="分类 ID")
    name: Optional[str] = Field(None, max_length=50, description="分类名称")
    description: Optional[str] = Field(None, max_length=255, description="分类描述")
    sort: Optional[int] = Field(None, description="排序")


class CategoryQueryRequest(PageRequest):
    """分类分页查询请求"""
    name: Optional[str] = Field(None, description="分类名称")


class CategoryVO(BaseModel):
    """分类视图对象"""
    id: int
    name: str
    description: Optional[str] = None
    sort: int
    article_count: int
    create_time: datetime = Field(..., alias="createTime")
    update_time: datetime = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True
