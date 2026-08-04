from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func
from sqlalchemy.dialects.mysql import TINYINT, LONGTEXT

from app.database import Base


class Article(Base):
    """博客文章表"""
    __tablename__ = 'blog_article'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="文章标题")
    summary = Column(String(500), comment="文章摘要")
    cover = Column(String(500), comment="封面图片")
    content = Column(LONGTEXT, nullable=False, comment="Markdown正文内容")
    category_id = Column(BigInteger, comment="分类ID")
    author_id = Column(BigInteger, comment="作者ID")
    status = Column(TINYINT, default=0, comment="状态 0草稿 1发布 2下架")
    is_top = Column(TINYINT, default=0, comment="是否置顶")
    is_original = Column(TINYINT, default=1, comment="是否原创")
    view_count = Column(Integer, default=0, comment="浏览次数")
    like_count = Column(Integer, default=0, comment="点赞数量")
    comment_count = Column(Integer, default=0, comment="评论数量")
    publish_time = Column(DateTime, comment="发布时间")
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
