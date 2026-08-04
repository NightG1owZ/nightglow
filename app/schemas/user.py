from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PageRequest


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=4, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, max_length=128, alias="password", description="密码")
    check_password: str = Field(..., min_length=8, max_length=128, alias="checkPassword", description="确认密码")

    class Config:
        populate_by_name = True


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=4, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, max_length=128, description="密码")


class UserAddRequest(BaseModel):
    """新增用户请求（管理员）"""
    username: str = Field(..., min_length=4, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像地址")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    status: Optional[int] = Field(default=1, description="状态 1正常 0禁用")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    id: int = Field(..., description="用户 ID")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=500, description="头像地址")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    status: Optional[int] = Field(None, description="状态 1正常 0禁用")
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="新密码（留空则不修改）")


class UserQueryRequest(PageRequest):
    """用户分页查询请求"""
    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    status: Optional[int] = Field(None, description="状态")


class UserVO(BaseModel):
    """用户视图对象"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    status: int
    last_login_time: Optional[datetime] = Field(None, alias="lastLoginTime")
    create_time: datetime = Field(..., alias="createTime")
    update_time: datetime = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True


class LoginUserVO(BaseModel):
    """当前登录用户视图对象"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    status: int
    last_login_time: Optional[datetime] = Field(None, alias="lastLoginTime")
    create_time: datetime = Field(..., alias="createTime")
    update_time: datetime = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True


class UserLoginVO(BaseModel):
    """登录返回对象"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        populate_by_name = True
