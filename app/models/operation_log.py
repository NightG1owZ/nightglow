from sqlalchemy import Column, BigInteger, String, Text, DateTime, func

from app.database import Base


class OperationLog(Base):
    """后台操作日志表"""
    __tablename__ = 'blog_operation_log'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    operation = Column(String(100), comment="操作名称")
    method = Column(String(200), comment="请求方法")
    params = Column(Text, comment="参数")
    ip = Column(String(50))
    create_time = Column(DateTime, server_default=func.now())
