from sqlalchemy import Column, BigInteger, String, Text, DateTime, func

from app.database import Base


class Config(Base):
    """网站配置表"""
    __tablename__ = 'blog_config'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(Text)
    description = Column(String(255))
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
