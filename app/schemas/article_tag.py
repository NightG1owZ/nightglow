from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class ArticleTagAddRequest(BaseModel):
    """新增文章标签关联请求"""
    article_id: int = Field(..., alias="articleId", description="文章ID")
    tag_id: int = Field(..., alias="tagId", description="标签ID")

    class Config:
        populate_by_name = True


class ArticleTagQueryRequest(PageRequest):
    """文章标签关联分页查询请求"""
    article_id: Optional[int] = Field(None, alias="articleId", description="文章ID")
    tag_id: Optional[int] = Field(None, alias="tagId", description="标签ID")


class ArticleTagVO(BaseModel):
    """文章标签关联视图对象"""
    id: int
    article_id: int = Field(..., alias="articleId")
    tag_id: int = Field(..., alias="tagId")
    create_time: datetime = Field(..., alias="createTime")

    class Config:
        populate_by_name = True
