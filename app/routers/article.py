from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.article import (
    ArticleAddRequest, ArticleUpdateRequest, ArticleQueryRequest, ArticleVO,
)
from app.services.article_service import ArticleService

router = APIRouter(prefix="/article", tags=["文章管理"])


@router.post("/list", response_model=BaseResponse[PageResponse[ArticleVO]])
async def list(
    request: ArticleQueryRequest,
    db: Database = Depends(get_db),
):
    """分页查询文章"""
    service = ArticleService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{article_id}", response_model=BaseResponse[ArticleVO])
async def get(
    article_id: int,
    db: Database = Depends(get_db),
):
    """查询单个文章"""
    service = ArticleService(db)
    vo = await service.get(article_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: ArticleAddRequest,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新增文章"""
    service = ArticleService(db)
    article_id = await service.add(request, author_id=current_user.id)
    return BaseResponse.success(data=article_id, message="新增成功")


@router.put("", response_model=BaseResponse[bool])
async def update(
    request: ArticleUpdateRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """更新文章"""
    service = ArticleService(db)
    await service.update(request)
    return BaseResponse.success(data=True, message="更新成功")


@router.delete("/{article_id}", response_model=BaseResponse[bool])
async def delete(
    article_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除文章"""
    service = ArticleService(db)
    await service.delete(article_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除文章"""
    service = ArticleService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
