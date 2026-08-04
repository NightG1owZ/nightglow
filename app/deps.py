import uuid
from typing import Optional

from databases import Database
from fastapi import Request, Depends
from sqlalchemy import select

from app.constants.user import UserConstant
from app.database import get_db
from app.exceptions import throw_if, ErrorCode, BusinessException
from app.models.user import User
from app.utils.session import get_session, set_session, remove_session


async def get_session_id(request: Request) -> Optional[str]:
    """从 Cookie 中读取 session_id"""
    return request.cookies.get(UserConstant.SESSION_COOKIE_NAME)


async def get_current_user(
    request: Request,
    db: Database = Depends(get_db),
) -> User:
    """获取当前登录用户，未登录抛出异常"""
    session_id = await get_session_id(request)
    throw_if(not session_id, ErrorCode.NOT_LOGIN_ERROR, "未登录")

    session = await get_session(session_id) if session_id else None
    throw_if(not session, ErrorCode.NOT_LOGIN_ERROR, "登录已过期，请重新登录")

    user_id = session.get("user_id")
    query = select(User).where(User.id == user_id)
    row = await db.fetch_one(query)
    throw_if(not row, ErrorCode.NOT_LOGIN_ERROR, "用户不存在")

    user = User(**dict(row))
    throw_if(user.status == UserConstant.STATUS_DISABLED, ErrorCode.USER_DISABLED, "账号已被禁用")
    return user


async def get_login_user_id(
    request: Request,
    db: Database = Depends(get_db),
) -> Optional[int]:
    """获取当前登录用户 ID，未登录返回 None（不抛异常）"""
    session_id = await get_session_id(request)
    if not session_id:
        return None
    session = await get_session(session_id) if session_id else None
    return session.get("user_id") if session else None


async def create_session(response, user_id: int, user: dict) -> str:
    """创建会话并写入 Cookie"""
    session_id = uuid.uuid4().hex
    await set_session(session_id, {"user_id": user_id, **user})
    response.set_cookie(
        key=UserConstant.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=None,  # session cookie
    )
    return session_id


async def clear_session(request: Request, response):
    """清除会话"""
    session_id = await get_session_id(request)
    if session_id:
        await remove_session(session_id)
    response.delete_cookie(UserConstant.SESSION_COOKIE_NAME)
