from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class ArticleLikeAddRequest(BaseModel):
    """新增文章点赞请求（IP 由服务端采集）"""
    article_id: int = Field(..., alias="articleId", description="文章ID")

    class Config:
        populate_by_name = True


class ArticleLikeCancelRequest(BaseModel):
    """取消文章点赞请求（按 IP 取消）"""
    article_id: int = Field(..., alias="articleId", description="文章ID")

    class Config:
        populate_by_name = True


class ArticleLikeQueryRequest(PageRequest):
    """文章点赞分页查询请求"""
    article_id: Optional[int] = Field(None, alias="articleId", description="文章ID")
    user_id: Optional[int] = Field(None, alias="userId", description="登录用户ID")


class ArticleLikeVO(BaseModel):
    """文章点赞视图对象"""
    id: int
    article_id: int = Field(..., alias="articleId")
    ip: Optional[str] = None
    user_id: Optional[int] = Field(None, alias="userId")
    create_time: datetime = Field(..., alias="createTime")

    class Config:
        populate_by_name = True
