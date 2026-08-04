from sqlalchemy import Column, BigInteger, String, DateTime, func

from app.database import Base


class ArticleLike(Base):
    """文章点赞记录表"""
    __tablename__ = 'blog_article_like'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_id = Column(BigInteger, nullable=False)
    ip = Column(String(50), comment="访问IP")
    user_id = Column(BigInteger, comment="登录用户ID")
    create_time = Column(DateTime, server_default=func.now())
