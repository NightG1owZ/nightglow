from sqlalchemy import Column, BigInteger, String, DateTime, func

from app.database import Base


class ArticleView(Base):
    """文章访问记录表"""
    __tablename__ = 'blog_article_view'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_id = Column(BigInteger, nullable=False)
    ip = Column(String(50))
    user_agent = Column(String(500))
    create_time = Column(DateTime, server_default=func.now())
