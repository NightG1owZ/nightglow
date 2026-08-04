from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.operation_log import (
    OperationLogAddRequest, OperationLogQueryRequest, OperationLogVO,
)
from app.services.operation_log_service import OperationLogService

router = APIRouter(prefix="/operation/log", tags=["操作日志"])


@router.post("/list", response_model=BaseResponse[PageResponse[OperationLogVO]])
async def list(
    request: OperationLogQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询操作日志"""
    service = OperationLogService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{log_id}", response_model=BaseResponse[OperationLogVO])
async def get(
    log_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个操作日志"""
    service = OperationLogService(db)
    vo = await service.get(log_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: OperationLogAddRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """新增操作日志"""
    service = OperationLogService(db)
    log_id = await service.add(request)
    return BaseResponse.success(data=log_id, message="新增成功")


@router.delete("/{log_id}", response_model=BaseResponse[bool])
async def delete(
    log_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除操作日志"""
    service = OperationLogService(db)
    await service.delete(log_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除操作日志"""
    service = OperationLogService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
