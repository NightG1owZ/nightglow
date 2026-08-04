from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class ArticleViewAddRequest(BaseModel):
    """新增文章浏览请求"""
    article_id: int = Field(..., alias="articleId", description="文章ID")
    ip: Optional[str] = Field(None, description="访问IP")
    user_agent: Optional[str] = Field(None, alias="userAgent", description="用户代理")

    class Config:
        populate_by_name = True


class ArticleViewQueryRequest(PageRequest):
    """文章浏览分页查询请求"""
    article_id: Optional[int] = Field(None, alias="articleId", description="文章ID")


class ArticleViewVO(BaseModel):
    """文章浏览视图对象"""
    id: int
    article_id: int = Field(..., alias="articleId")
    ip: Optional[str] = None
    user_agent: Optional[str] = Field(None, alias="userAgent")
    create_time: datetime = Field(..., alias="createTime")

    class Config:
        populate_by_name = True
