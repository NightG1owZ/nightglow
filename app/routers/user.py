from fastapi import APIRouter, Depends, Response, Request
from databases import Database

from app.database import get_db
from app.deps import get_current_user, create_session, clear_session
from app.models.user import User
from app.schemas.common import BaseResponse, PageResponse, BatchDeleteRequest
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserAddRequest,
    UserUpdateRequest, UserQueryRequest, UserVO, LoginUserVO, UserLoginVO,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.post("/register", response_model=BaseResponse[int])
async def register(
    request: UserRegisterRequest,
    db: Database = Depends(get_db),
):
    """用户注册"""
    service = UserService(db)
    user_id = await service.register(request)
    return BaseResponse.success(data=user_id, message="注册成功")


@router.post("/login", response_model=BaseResponse[UserLoginVO])
async def login(
    request: UserLoginRequest,
    response: Response,
    db: Database = Depends(get_db),
):
    """用户登录"""
    service = UserService(db)
    user_id, login_vo = await service.login(request)
    await create_session(response, user_id, {"username": login_vo.username})
    return BaseResponse.success(data=login_vo, message="登录成功")


@router.post("/logout", response_model=BaseResponse[bool])
async def logout(
    request: Request,
    response: Response,
):
    """退出登录"""
    await clear_session(request, response)
    return BaseResponse.success(data=True, message="已退出登录")


@router.get("/current", response_model=BaseResponse[LoginUserVO])
async def current(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    """获取当前登录用户信息"""
    service = UserService(db)
    vo = await service.get_login_user_vo(current_user.id)
    return BaseResponse.success(data=vo)


@router.post("/list", response_model=BaseResponse[PageResponse[UserVO]])
async def list(
    request: UserQueryRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """分页查询用户"""
    service = UserService(db)
    records, total = await service.page(request)
    return BaseResponse.success(data=PageResponse.of(records, total, request.current, request.page_size))


@router.get("/{user_id}", response_model=BaseResponse[UserVO])
async def get(
    user_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """查询单个用户"""
    service = UserService(db)
    vo = await service.get(user_id)
    return BaseResponse.success(data=vo)


@router.post("", response_model=BaseResponse[int])
async def add(
    request: UserAddRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """新增用户"""
    service = UserService(db)
    user_id = await service.add(request)
    return BaseResponse.success(data=user_id, message="新增成功")


@router.put("", response_model=BaseResponse[bool])
async def update(
    request: UserUpdateRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """更新用户"""
    service = UserService(db)
    await service.update(request)
    return BaseResponse.success(data=True, message="更新成功")


@router.delete("/{user_id}", response_model=BaseResponse[bool])
async def delete(
    user_id: int,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除用户"""
    service = UserService(db)
    await service.delete(user_id)
    return BaseResponse.success(data=True, message="删除成功")


@router.post("/batch/delete", response_model=BaseResponse[int])
async def batch_delete(
    request: BatchDeleteRequest,
    db: Database = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除用户"""
    service = UserService(db)
    count = await service.batch_delete(request.ids)
    return BaseResponse.success(data=count, message="批量删除成功")
