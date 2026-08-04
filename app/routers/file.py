from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.file import (
    FileAddRequest, FileUpdateRequest, FileQueryRequest, FileVO,
)
from app.services.file_service import FileService

router = APIRouter(prefix="/file", tags=["文件管理"])


@router.post("/list", response_model=BaseResponse[PageResponse[FileVO]])
async def list(
    request: FileQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询文件"""
    service = FileService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{file_id}", response_model=BaseResponse[FileVO])
async def get(
    file_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个文件"""
    service = FileService(db)
    vo = await service.get(file_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: FileAddRequest,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新增文件"""
    service = FileService(db)
    file_id = await service.add(request, uploader_id=current_user.id)
    return BaseResponse.success(data=file_id, message="新增成功")


@router.put("", response_model=BaseResponse[bool])
async def update(
    request: FileUpdateRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """更新文件"""
    service = FileService(db)
    await service.update(request)
    return BaseResponse.success(data=True, message="更新成功")


@router.delete("/{file_id}", response_model=BaseResponse[bool])
async def delete(
    file_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除文件"""
    service = FileService(db)
    await service.delete(file_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除文件"""
    service = FileService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
