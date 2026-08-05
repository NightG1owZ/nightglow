from fastapi import APIRouter, Depends, Request
from databases import Database

from app.database import get_db
from app.deps import get_current_user, get_login_user_id
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.article_like import (
    ArticleLikeAddRequest, ArticleLikeCancelRequest, ArticleLikeQueryRequest, ArticleLikeVO,
)
from app.services.article_like_service import ArticleLikeService
from app.utils.request import get_client_ip

router = APIRouter(prefix="/article/like", tags=["文章点赞"])


@router.post("/list", response_model=BaseResponse[PageResponse[ArticleLikeVO]])
async def list(
    request: ArticleLikeQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询文章点赞"""
    service = ArticleLikeService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{like_id}", response_model=BaseResponse[ArticleLikeVO])
async def get(
    like_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个文章点赞"""
    service = ArticleLikeService(db)
    vo = await service.get(like_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: ArticleLikeAddRequest,
    req: Request,
    db: Database = Depends(get_db),
    user_id: int = Depends(get_login_user_id),
):
    """点赞文章（基于 IP 去重，点赞数 +1）"""
    service = ArticleLikeService(db)
    like_id = await service.add(request, ip=get_client_ip(req), user_id=user_id)
    return BaseResponse.success(data=like_id, message="点赞成功")


@router.post("/cancel", response_model=BaseResponse[bool])
async def cancel(
    request: ArticleLikeCancelRequest,
    req: Request,
    db: Database = Depends(get_db),
):
    """取消点赞（按 IP 取消，点赞数 -1）"""
    service = ArticleLikeService(db)
    ok = await service.cancel(request.article_id, ip=get_client_ip(req))
    return BaseResponse.success(data=ok, message="已取消点赞" if ok else "无点赞记录")


@router.delete("/{like_id}", response_model=BaseResponse[bool])
async def delete(
    like_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除文章点赞（点赞数 -1）"""
    service = ArticleLikeService(db)
    await service.delete(like_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除文章点赞"""
    service = ArticleLikeService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
