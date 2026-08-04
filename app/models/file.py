from sqlalchemy import Column, BigInteger, String, DateTime, func

from app.database import Base


class File(Base):
    """博客文件资源表"""
    __tablename__ = 'blog_file'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    filename = Column(String(255), comment="文件名称")
    url = Column(String(500), comment="访问地址")
    size = Column(BigInteger, comment="文件大小")
    type = Column(String(50), comment="文件类型")
    uploader_id = Column(BigInteger, comment="上传用户")
    create_time = Column(DateTime, server_default=func.now())
