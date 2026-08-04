from typing import Optional, Tuple, List, Dict, Any

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.operation_log import OperationLog
from app.schemas.operation_log import (
    OperationLogAddRequest, OperationLogQueryRequest, OperationLogVO,
)


class OperationLogService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, log_id: int):
        row = await self.db.fetch_one(select(OperationLog).where(OperationLog.id == log_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "日志不存在")
        return row

    async def get(self, log_id: int) -> OperationLogVO:
        row = await self._get_row(log_id)
        return OperationLogVO(**dict(row))

    async def add(self, request: OperationLogAddRequest) -> int:
        log_id = await self.db.execute(
            insert(OperationLog).values(
                operation=request.operation,
                method=request.method,
                params=request.params,
                ip=request.ip,
                user_id=request.user_id,
            )
        )
        return log_id

    async def delete(self, log_id: int) -> None:
        await self._get_row(log_id)
        await self.db.execute(delete(OperationLog).where(OperationLog.id == log_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(OperationLog).where(OperationLog.id.in_(ids)))
        return result

    async def page(self, request: OperationLogQueryRequest) -> Tuple[List[OperationLogVO], int]:
        conditions = []
        if request.user_id is not None:
            conditions.append(OperationLog.user_id == request.user_id)
        if request.operation:
            conditions.append(OperationLog.operation.like(f"%{request.operation}%"))

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(OperationLog.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(OperationLog)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(OperationLog.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [OperationLogVO(**dict(r)) for r in rows]
        return records, total
