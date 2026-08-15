from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class TagAddRequest(BaseModel):
    """新增标签请求"""
    name: str = Field(..., max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")
    parent_id: int = Field(default=0, alias="parentId", description="父标签ID，0表示顶级标签")

    class Config:
        populate_by_name = True


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
    parent_id: int = Field(alias="parentId")
    level: int
    article_count: int
    create_time: datetime = Field(..., alias="createTime")
    update_time: datetime = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True


class TagArticleVO(BaseModel):
    """标签节点下关联的文章摘要"""
    id: int
    title: str
    summary: Optional[str] = None
    cover: Optional[str] = None
    publish_time: Optional[datetime] = Field(None, alias="publishTime")
    create_time: datetime = Field(..., alias="createTime")

    class Config:
        populate_by_name = True


class TagTreeVO(BaseModel):
    """标签树形视图对象（每个节点含直接关联的文章列表）"""
    id: int
    name: str
    color: Optional[str] = None
    parent_id: int = Field(alias="parentId")
    level: int
    article_count: int = Field(alias="articleCount")
    articles: List["TagArticleVO"] = Field(default_factory=list)
    children: List["TagTreeVO"] = Field(default_factory=list)

    class Config:
        populate_by_name = True


TagTreeVO.model_rebuild()
