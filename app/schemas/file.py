from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class FileAddRequest(BaseModel):
    """新增文件请求"""
    filename: str = Field(..., max_length=255, description="文件名称")
    url: str = Field(..., max_length=500, description="访问地址")
    size: Optional[int] = Field(None, description="文件大小")
    type: Optional[str] = Field(None, max_length=50, description="文件类型")


class FileUpdateRequest(BaseModel):
    """更新文件请求"""
    id: int = Field(..., description="文件 ID")
    filename: Optional[str] = Field(None, max_length=255, description="文件名称")
    url: Optional[str] = Field(None, max_length=500, description="访问地址")


class FileQueryRequest(PageRequest):
    """文件分页查询请求"""
    filename: Optional[str] = Field(None, description="文件名称")
    type: Optional[str] = Field(None, description="文件类型")


class FileVO(BaseModel):
    """文件视图对象"""
    id: int
    filename: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    type: Optional[str] = None
    uploader_id: Optional[int] = Field(None, alias="uploaderId")
    create_time: datetime = Field(..., alias="createTime")

    class Config:
        populate_by_name = True
