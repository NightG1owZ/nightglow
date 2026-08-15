from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class ArticleAddRequest(BaseModel):
    """新增文章请求"""
    title: str = Field(..., max_length=200, description="文章标题")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    cover: Optional[str] = Field(None, max_length=500, description="封面图片")
    content: str = Field(..., description="Markdown正文内容")
    category_id: Optional[int] = Field(None, alias="categoryId", description="分类ID")
    status: int = Field(default=0, description="状态 0草稿 1发布 2下架")
    is_top: int = Field(default=0, alias="isTop", description="是否置顶")
    is_original: int = Field(default=1, alias="isOriginal", description="是否原创")
    publish_time: Optional[datetime] = Field(None, alias="publishTime", description="发布时间")
    tag_ids: List[int] = Field(default_factory=list, alias="tagIds", description="标签ID列表")

    class Config:
        populate_by_name = True


class ArticleUpdateRequest(BaseModel):
    """更新文章请求"""
    id: int = Field(..., description="文章 ID")
    title: Optional[str] = Field(None, max_length=200, description="文章标题")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    cover: Optional[str] = Field(None, max_length=500, description="封面图片")
    content: Optional[str] = Field(None, description="Markdown正文内容")
    category_id: Optional[int] = Field(None, alias="categoryId", description="分类ID")
    status: Optional[int] = Field(None, description="状态 0草稿 1发布 2下架")
    is_top: Optional[int] = Field(None, alias="isTop", description="是否置顶")
    is_original: Optional[int] = Field(None, alias="isOriginal", description="是否原创")
    publish_time: Optional[datetime] = Field(None, alias="publishTime", description="发布时间")
    tag_ids: Optional[List[int]] = Field(None, alias="tagIds", description="标签ID列表")

    class Config:
        populate_by_name = True


class ArticleQueryRequest(PageRequest):
    """文章分页查询请求"""
    title: Optional[str] = Field(None, description="文章标题")
    category_id: Optional[int] = Field(None, alias="categoryId", description="分类ID")
    tag_id: Optional[int] = Field(None, alias="tagId", description="标签ID（含其所有子标签）")
    status: Optional[int] = Field(None, description="状态")
    is_top: Optional[int] = Field(None, alias="isTop", description="是否置顶")


class ArticleVO(BaseModel):
    """文章视图对象"""
    id: int
    title: str
    summary: Optional[str] = None
    cover: Optional[str] = None
    content: str
    category_id: Optional[int] = Field(None, alias="categoryId")
    author_id: Optional[int] = Field(None, alias="authorId")
    status: int
    is_top: int = Field(0, alias="isTop")
    is_original: int = Field(1, alias="isOriginal")
    view_count: Optional[int] = Field(0, alias="viewCount")
    like_count: Optional[int] = Field(0, alias="likeCount")
    comment_count: Optional[int] = Field(0, alias="commentCount")
    publish_time: Optional[datetime] = Field(None, alias="publishTime")
    create_time: datetime = Field(..., alias="createTime")
    update_time: datetime = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True
