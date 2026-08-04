from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func

from app.database import Base


class Tag(Base):
    """文章标签表"""
    __tablename__ = 'blog_tag'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, comment="标签名称")
    color = Column(String(20), comment="标签颜色")
    article_count = Column(Integer, default=0, comment="文章数量")
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
