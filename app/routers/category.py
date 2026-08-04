from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.category import (
    CategoryAddRequest, CategoryUpdateRequest, CategoryQueryRequest, CategoryVO,
)
from app.services.category_service import CategoryService

router = APIRouter(prefix="/category", tags=["分类管理"])


@router.post("/list", response_model=BaseResponse[PageResponse[CategoryVO]])
async def list(
    request: CategoryQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询分类"""
    service = CategoryService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{category_id}", response_model=BaseResponse[CategoryVO])
async def get(
    category_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个分类"""
    service = CategoryService(db)
    vo = await service.get(category_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: CategoryAddRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """新增分类"""
    service = CategoryService(db)
    category_id = await service.add(request)
    return BaseResponse.success(data=category_id, message="新增成功")


@router.put("", response_model=BaseResponse[bool])
async def update(
    request: CategoryUpdateRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """更新分类"""
    service = CategoryService(db)
    await service.update(request)
    return BaseResponse.success(data=True, message="更新成功")


@router.delete("/{category_id}", response_model=BaseResponse[bool])
async def delete(
    category_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除分类"""
    service = CategoryService(db)
    await service.delete(category_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除分类"""
    service = CategoryService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
