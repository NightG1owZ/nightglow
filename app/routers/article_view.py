from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.article_view import ArticleViewAddRequest, ArticleViewQueryRequest, ArticleViewVO
from app.services.article_view_service import ArticleViewService

router = APIRouter(prefix="/article/view", tags=["文章浏览"])


@router.post("/list", response_model=BaseResponse[PageResponse[ArticleViewVO]])
async def list(
    request: ArticleViewQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询文章浏览"""
    service = ArticleViewService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{view_id}", response_model=BaseResponse[ArticleViewVO])
async def get(
    view_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个文章浏览"""
    service = ArticleViewService(db)
    vo = await service.get(view_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: ArticleViewAddRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """新增文章浏览"""
    service = ArticleViewService(db)
    view_id = await service.add(request)
    return BaseResponse.success(data=view_id, message="新增成功")


@router.delete("/{view_id}", response_model=BaseResponse[bool])
async def delete(
    view_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除文章浏览"""
    service = ArticleViewService(db)
    await service.delete(view_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除文章浏览"""
    service = ArticleViewService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
