from sqlalchemy import Column, BigInteger, String, DateTime, func

from app.database import Base
from sqlalchemy.dialects.mysql import TINYINT


class User(Base):
    """博客用户表"""
    __tablename__ = 'blog_user'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), nullable=True, unique=True, comment="用户名(账号密码登录使用，微信扫码注册用户可为空)")
    password = Column(String(255), nullable=True, comment="密码密文(账号密码登录使用，微信扫码注册用户可为空)")
    nickname = Column(String(50), comment="昵称")
    avatar = Column(String(500), comment="头像地址")
    email = Column(String(100), comment="邮箱")
    openid = Column(String(64), unique=True, comment="微信唯一标识openid")
    unionid = Column(String(64), unique=True, comment="微信开放平台unionid(同一开放平台下唯一)")
    wechat_nickname = Column(String(100), comment="微信昵称")
    wechat_avatar = Column(String(500), comment="微信头像")
    wechat_login_status = Column(TINYINT, default=0, comment="微信扫码登录状态 1已登录 0未登录")
    last_wechat_login_time = Column(DateTime, comment="微信最后登录时间")
    status = Column(TINYINT, default=1, comment="状态 1正常 0禁用")
    last_login_time = Column(DateTime, comment="最后登录时间")
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
