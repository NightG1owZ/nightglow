from datetime import datetime
from typing import Optional, Tuple, List, Any, Dict

from databases import Database
from sqlalchemy import select, func, and_, or_, insert, update, delete

from app.config import settings
from app.constants.user import UserConstant
from app.exceptions import throw_if, ErrorCode
from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserAddRequest,
    UserUpdateRequest, UserQueryRequest, UserVO, LoginUserVO, UserLoginVO,
)
from app.utils.password import encrypt_password, verify_password
from app.utils.wechat import get_access_token, get_user_info


def _row_to_dict(row) -> Dict[str, Any]:
    data = dict(row)
    data.pop("password", None)
    return data


class UserService:
    def __init__(self, db: Database):
        self.db = db

    # ==================== 认证 ====================

    async def register(self, request: UserRegisterRequest) -> int:
        throw_if(len(request.username) < 4, ErrorCode.PARAMS_ERROR, "用户名长度不能小于 4 位")
        throw_if(len(request.password) < 8, ErrorCode.PARAMS_ERROR, "密码长度不能小于 8 位")
        throw_if(request.password != request.check_password, ErrorCode.PARAMS_ERROR, "两次输入的密码不一致")

        # 校验用户名是否已存在
        count = await self.db.fetch_val(
            select(func.count(User.id)).where(User.username == request.username)
        )
        throw_if(count > 0, ErrorCode.USER_ALREADY_EXIST, "用户名已存在")

        user_id = await self.db.execute(
            insert(User).values(
                username=request.username,
                password=encrypt_password(request.password),
                nickname=request.nickname or f"用户{request.username}",
                status=UserConstant.STATUS_NORMAL,
            )
        )
        return user_id

    async def login(self, request: UserLoginRequest) -> Tuple[int, UserLoginVO]:
        row = await self.db.fetch_one(
            select(User).where(User.username == request.username)
        )
        throw_if(not row, ErrorCode.LOGIN_ERROR, "账号或密码错误")

        user = dict(row)
        throw_if(not verify_password(request.password, user["password"]), ErrorCode.LOGIN_ERROR, "账号或密码错误")
        throw_if(user["status"] == UserConstant.STATUS_DISABLED, ErrorCode.USER_DISABLED, "账号已被禁用")

        # 更新最后登录时间
        await self.db.execute(
            update(User).where(User.id == user["id"]).values(last_login_time=datetime.now())
        )

        login_vo = UserLoginVO(
            id=user["id"],
            username=user["username"],
            nickname=user.get("nickname"),
            avatar=user.get("avatar"),
        )
        return user["id"], login_vo

    async def wechat_login(self, code: str) -> Tuple[int, UserLoginVO]:
        """微信扫码登录：用 code 换取 openid 与用户信息，未注册则自动注册并登录"""
        token_data = await get_access_token(settings.wechat_app_id, settings.wechat_app_secret, code)
        throw_if(token_data.get("errcode"), ErrorCode.OPERATION_ERROR, token_data.get("errmsg") or "微信授权失败")

        openid = token_data.get("openid")
        throw_if(not openid, ErrorCode.OPERATION_ERROR, "获取微信身份失败")

        unionid = token_data.get("unionid")
        wechat_nickname = None
        wechat_avatar = None
        access_token = token_data.get("access_token")
        if access_token:
            userinfo = await get_user_info(access_token, openid)
            if not userinfo.get("errcode"):
                wechat_nickname = userinfo.get("nickname")
                wechat_avatar = userinfo.get("headimgurl")
                unionid = unionid or userinfo.get("unionid")

        now = datetime.now()
        row = await self.db.fetch_one(select(User).where(User.openid == openid))
        if row:
            user_id = dict(row)["id"]
            await self.db.execute(
                update(User).where(User.id == user_id).values(
                    unionid=unionid,
                    wechat_nickname=wechat_nickname,
                    wechat_avatar=wechat_avatar,
                    wechat_login_status=1,
                    last_wechat_login_time=now,
                )
            )
        else:
            user_id = await self.db.execute(
                insert(User).values(
                    username=None,
                    password=None,
                    nickname=wechat_nickname,
                    avatar=wechat_avatar,
                    openid=openid,
                    unionid=unionid,
                    wechat_nickname=wechat_nickname,
                    wechat_avatar=wechat_avatar,
                    wechat_login_status=1,
                    last_wechat_login_time=now,
                    status=UserConstant.STATUS_NORMAL,
                )
            )

        user = dict(await self._get_row(user_id))
        login_vo = UserLoginVO(
            id=user["id"],
            username=user.get("username"),
            nickname=user.get("nickname") or user.get("wechat_nickname"),
            avatar=user.get("avatar") or user.get("wechat_avatar"),
        )
        return user_id, login_vo

    async def get_login_user_vo(self, user_id: int) -> LoginUserVO:
        row = await self._get_row(user_id)
        return LoginUserVO(**_row_to_dict(row))

    # ==================== CRUD ====================

    async def _get_row(self, user_id: int):
        row = await self.db.fetch_one(select(User).where(User.id == user_id))
        throw_if(not row, ErrorCode.USER_NOT_EXIST, "用户不存在")
        return row

    async def get(self, user_id: int) -> UserVO:
        row = await self._get_row(user_id)
        return UserVO(**_row_to_dict(row))

    async def add(self, request: UserAddRequest) -> int:
        count = await self.db.fetch_val(
            select(func.count(User.id)).where(User.username == request.username)
        )
        throw_if(count > 0, ErrorCode.USER_ALREADY_EXIST, "用户名已存在")

        user_id = await self.db.execute(
            insert(User).values(
                username=request.username,
                password=encrypt_password(request.password),
                nickname=request.nickname or f"用户{request.username}",
                avatar=request.avatar,
                email=request.email,
                status=request.status if request.status is not None else UserConstant.STATUS_NORMAL,
            )
        )
        return user_id

    async def update(self, request: UserUpdateRequest) -> None:
        await self._get_row(request.id)
        values: Dict[str, Any] = {}
        for key in ("nickname", "avatar", "email", "status"):
            val = getattr(request, key)
            if val is not None:
                values[key] = val
        if request.password:
            values["password"] = encrypt_password(request.password)
        throw_if(not values, ErrorCode.PARAMS_ERROR, "无更新字段")
        await self.db.execute(update(User).where(User.id == request.id).values(**values))

    async def delete(self, user_id: int) -> None:
        await self._get_row(user_id)
        await self.db.execute(delete(User).where(User.id == user_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(User).where(User.id.in_(ids)))
        return result

    async def page(self, request: UserQueryRequest) -> Tuple[List[UserVO], int]:
        conditions = []
        if request.username:
            conditions.append(User.username.like(f"%{request.username}%"))
        if request.nickname:
            conditions.append(User.nickname.like(f"%{request.nickname}%"))
        if request.status is not None:
            conditions.append(User.status == request.status)

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(User.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(User)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(User.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [UserVO(**_row_to_dict(r)) for r in rows]
        return records, total
