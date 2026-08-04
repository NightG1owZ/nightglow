from sqlalchemy import Column, BigInteger, DateTime, func

from app.database import Base


class ArticleTag(Base):
    """文章标签关联表"""
    __tablename__ = 'blog_article_tag'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_id = Column(BigInteger, nullable=False, comment="文章ID")
    tag_id = Column(BigInteger, nullable=False, comment="标签ID")
    create_time = Column(DateTime, server_default=func.now())
