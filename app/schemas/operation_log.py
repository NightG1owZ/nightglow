from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class OperationLogAddRequest(BaseModel):
    """新增操作日志请求"""
    operation: str = Field(..., max_length=100, description="操作名称")
    method: Optional[str] = Field(None, max_length=200, description="请求方法")
    params: Optional[str] = Field(None, description="参数")
    ip: Optional[str] = Field(None, max_length=50, description="IP 地址")
    user_id: Optional[int] = Field(None, alias="userId", description="用户 ID")

    class Config:
        populate_by_name = True


class OperationLogQueryRequest(PageRequest):
    """操作日志分页查询请求"""
    user_id: Optional[int] = Field(None, alias="userId", description="用户 ID")
    operation: Optional[str] = Field(None, description="操作名称")


class OperationLogVO(BaseModel):
    """操作日志视图对象"""
    id: int
    user_id: Optional[int] = Field(None, alias="userId")
    operation: Optional[str] = None
    method: Optional[str] = None
    params: Optional[str] = None
    ip: Optional[str] = None
    create_time: datetime = Field(..., alias="createTime")

    class Config:
        populate_by_name = True
