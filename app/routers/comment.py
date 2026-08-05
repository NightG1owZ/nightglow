from fastapi import APIRouter, Depends, Request
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.comment import (
    CommentAddRequest, CommentUpdateRequest, CommentQueryRequest, CommentVO,
)
from app.services.comment_service import CommentService
from app.utils.request import get_client_ip, get_user_agent

router = APIRouter(prefix="/comment", tags=["评论管理"])


@router.post("/list", response_model=BaseResponse[PageResponse[CommentVO]])
async def list(
    request: CommentQueryRequest,
    db: Database = Depends(get_db),
):
    """分页查询评论"""
    service = CommentService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{comment_id}", response_model=BaseResponse[CommentVO])
async def get(
    comment_id: int,
    db: Database = Depends(get_db),
):
    """查询单个评论"""
    service = CommentService(db)
    vo = await service.get(comment_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: CommentAddRequest,
    req: Request,
    db: Database = Depends(get_db),
):
    """新增评论（自动采集 IP 与 User-Agent）"""
    service = CommentService(db)
    comment_id = await service.add(request, ip=get_client_ip(req), user_agent=get_user_agent(req))
    return BaseResponse.success(data=comment_id, message="新增成功")


@router.put("", response_model=BaseResponse[bool])
async def update(
    request: CommentUpdateRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """更新评论"""
    service = CommentService(db)
    await service.update(request)
    return BaseResponse.success(data=True, message="更新成功")


@router.delete("/{comment_id}", response_model=BaseResponse[bool])
async def delete(
    comment_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除评论"""
    service = CommentService(db)
    await service.delete(comment_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除评论"""
    service = CommentService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
