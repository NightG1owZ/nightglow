from sqlalchemy import Column, BigInteger, String, DateTime, func

from app.database import Base
from sqlalchemy.dialects.mysql import TINYINT


class User(Base):
    """博客用户表"""
    __tablename__ = 'blog_user'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), nullable=False, unique=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码密文")
    nickname = Column(String(50), comment="昵称")
    avatar = Column(String(500), comment="头像地址")
    email = Column(String(100), comment="邮箱")
    status = Column(TINYINT, default=1, comment="状态 1正常 0禁用")
    last_login_time = Column(DateTime, comment="最后登录时间")
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
