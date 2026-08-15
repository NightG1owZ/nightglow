from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class CommentAddRequest(BaseModel):
    """新增评论请求（IP/User-Agent 与用户身份由服务端采集，昵称/邮箱/头像忽略客户端输入）"""
    article_id: int = Field(..., alias="articleId", description="文章ID")
    parent_id: int = Field(default=0, alias="parentId", description="父评论ID")
    content: str = Field(..., max_length=1000, description="评论内容")

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
