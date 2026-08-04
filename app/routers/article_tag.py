from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.article_tag import ArticleTagAddRequest, ArticleTagQueryRequest, ArticleTagVO
from app.services.article_tag_service import ArticleTagService

router = APIRouter(prefix="/article/tag", tags=["文章标签关联"])


@router.post("/list", response_model=BaseResponse[PageResponse[ArticleTagVO]])
async def list(
    request: ArticleTagQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询文章标签关联"""
    service = ArticleTagService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{article_tag_id}", response_model=BaseResponse[ArticleTagVO])
async def get(
    article_tag_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个文章标签关联"""
    service = ArticleTagService(db)
    vo = await service.get(article_tag_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: ArticleTagAddRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """新增文章标签关联"""
    service = ArticleTagService(db)
    article_tag_id = await service.add(request)
    return BaseResponse.success(data=article_tag_id, message="新增成功")


@router.delete("/{article_tag_id}", response_model=BaseResponse[bool])
async def delete(
    article_tag_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除文章标签关联"""
    service = ArticleTagService(db)
    await service.delete(article_tag_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除文章标签关联"""
    service = ArticleTagService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
