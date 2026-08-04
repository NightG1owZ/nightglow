from fastapi import APIRouter, Depends
from databases import Database

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.config import (
    ConfigAddRequest, ConfigUpdateRequest, ConfigQueryRequest, ConfigVO,
)
from app.services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["网站配置"])


@router.post("/list", response_model=BaseResponse[PageResponse[ConfigVO]])
async def list(
    request: ConfigQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询网站配置"""
    service = ConfigService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/key/{config_key}", response_model=BaseResponse[ConfigVO])
async def get_by_key(
    config_key: str,
    db: Database = Depends(get_db),
):
    """根据配置键查询配置"""
    service = ConfigService(db)
    vo = await service.get_by_key(config_key)
    return BaseResponse.success(data=vo)


@router.get("/{config_id}", response_model=BaseResponse[ConfigVO])
async def get(
    config_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个配置"""
    service = ConfigService(db)
    vo = await service.get(config_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: ConfigAddRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """新增配置"""
    service = ConfigService(db)
    config_id = await service.add(request)
    return BaseResponse.success(data=config_id, message="新增成功")


@router.put("", response_model=BaseResponse[bool])
async def update(
    request: ConfigUpdateRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """更新配置"""
    service = ConfigService(db)
    await service.update(request)
    return BaseResponse.success(data=True, message="更新成功")


@router.delete("/{config_id}", response_model=BaseResponse[bool])
async def delete(
    config_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除配置"""
    service = ConfigService(db)
    await service.delete(config_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除配置"""
    service = ConfigService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
