from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class CommentAddRequest(BaseModel):
    """新增评论请求"""
    article_id: int = Field(..., alias="articleId", description="文章ID")
    parent_id: int = Field(default=0, alias="parentId", description="父评论ID")
    nickname: str = Field(..., max_length=50, description="评论昵称")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    avatar: Optional[str] = Field(None, max_length=500, description="头像")
    content: str = Field(..., max_length=1000, description="评论内容")
    ip: Optional[str] = Field(None, max_length=50, description="IP地址")
    user_agent: Optional[str] = Field(None, max_length=500, alias="userAgent", description="浏览器信息")

    class Config:
        populate_by_name = True


class CommentUpdateRequest(BaseModel):
    """更新评论请求"""
    id: int = Field(..., description="评论 ID")
    status: Optional[int] = Field(None, description="状态 1显示 0隐藏")


class CommentQueryRequest(PageRequest):
    """评论分页查询请求"""
    article_id: Optional[int] = Field(None, alias="articleId", description="文章ID")
    status: Optional[int] = Field(None, description="状态")

    class Config:
        populate_by_name = True


class CommentVO(BaseModel):
    """评论视图对象"""
    id: int
    article_id: int = Field(..., alias="articleId")
    parent_id: int = Field(..., alias="parentId")
    nickname: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    content: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = Field(None, alias="userAgent")
    status: int
    create_time: datetime = Field(..., alias="createTime")

    class Config:
        populate_by_name = True
