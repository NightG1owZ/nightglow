from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class ConfigAddRequest(BaseModel):
    """新增网站配置请求"""
    config_key: str = Field(..., max_length=100, alias="configKey", description="配置键")
    config_value: Optional[str] = Field(None, alias="configValue", description="配置值")
    description: Optional[str] = Field(None, max_length=255, description="描述")

    class Config:
        populate_by_name = True


class ConfigUpdateRequest(BaseModel):
    """更新网站配置请求"""
    id: int = Field(..., description="配置 ID")
    config_value: Optional[str] = Field(None, alias="configValue", description="配置值")
    description: Optional[str] = Field(None, max_length=255, description="描述")

    class Config:
        populate_by_name = True


class ConfigQueryRequest(PageRequest):
    """网站配置分页查询请求"""
    config_key: Optional[str] = Field(None, alias="configKey", description="配置键")


class ConfigVO(BaseModel):
    """网站配置视图对象"""
    id: int
    config_key: str = Field(..., alias="configKey")
    config_value: Optional[str] = Field(None, alias="configValue")
    description: Optional[str] = None
    create_time: datetime = Field(..., alias="createTime")
    update_time: datetime = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True
