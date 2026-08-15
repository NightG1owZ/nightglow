from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func
from sqlalchemy.dialects.mysql import TINYINT

from app.database import Base


class Tag(Base):
    """文章标签表"""
    __tablename__ = 'blog_tag'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="标签名称")
    color = Column(String(20), comment="标签颜色")
    parent_id = Column(BigInteger, default=0, comment="父标签ID，0表示顶级标签")
    level = Column(TINYINT, default=1, comment="标签层级深度，1为顶级标签")
    article_count = Column(Integer, default=0, comment="文章数量")
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
