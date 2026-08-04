from sqlalchemy import Column, BigInteger, String, DateTime, func
from sqlalchemy.dialects.mysql import TINYINT

from app.database import Base


class Comment(Base):
    """文章评论表"""
    __tablename__ = 'blog_comment'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_id = Column(BigInteger, nullable=False, comment="文章ID")
    parent_id = Column(BigInteger, default=0, comment="父评论ID")
    nickname = Column(String(50), comment="评论昵称")
    email = Column(String(100), comment="邮箱")
    avatar = Column(String(500), comment="头像")
    content = Column(String(1000), comment="评论内容")
    ip = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="浏览器信息")
    status = Column(TINYINT, default=1, comment="状态 1显示 0隐藏")
    create_time = Column(DateTime, server_default=func.now())
