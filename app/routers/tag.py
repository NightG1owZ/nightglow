from typing import List

from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.tag import (
    TagAddRequest, TagUpdateRequest, TagQueryRequest, TagVO, TagTreeVO,
)
from app.services.tag_service import TagService

router = APIRouter(prefix="/tag", tags=["标签管理"])


@router.get("/tree", response_model=BaseResponse[List[TagTreeVO]])
async def tree(db: Database = Depends(get_db)):
    """查询标签层级树（公开，供 /categories 页面使用）"""
    service = TagService(db)
    return BaseResponse.success(data=await service.tree())


@router.post("/list", response_model=BaseResponse[PageResponse[TagVO]])
async def list(
    request: TagQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询标签"""
    service = TagService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{tag_id}", response_model=BaseResponse[TagVO])
async def get(
    tag_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个标签"""
    service = TagService(db)
    vo = await service.get(tag_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: TagAddRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """新增标签"""
    service = TagService(db)
    tag_id = await service.add(request)
    return BaseResponse.success(data=tag_id, message="新增成功")


@router.put("", response_model=BaseResponse[bool])
async def update(
    request: TagUpdateRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """更新标签"""
    service = TagService(db)
    await service.update(request)
    return BaseResponse.success(data=True, message="更新成功")


@router.delete("/{tag_id}", response_model=BaseResponse[bool])
async def delete(
    tag_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除标签"""
    service = TagService(db)
    await service.delete(tag_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除标签"""
    service = TagService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
