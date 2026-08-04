from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func

from app.database import Base


class Category(Base):
    """文章分类表"""
    __tablename__ = 'blog_category'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="分类名称")
    description = Column(String(255), comment="分类描述")
    sort = Column(Integer, default=0, comment="排序")
    article_count = Column(Integer, default=0, comment="文章数量")
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
