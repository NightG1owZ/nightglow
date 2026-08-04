from typing import Optional, Tuple, List, Any, Dict

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.tag import Tag
from app.schemas.tag import (
    TagAddRequest, TagUpdateRequest, TagQueryRequest, TagVO,
)


class TagService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, tag_id: int):
        row = await self.db.fetch_one(select(Tag).where(Tag.id == tag_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "标签不存在")
        return row

    async def get(self, tag_id: int) -> TagVO:
        row = await self._get_row(tag_id)
        return TagVO(**dict(row))

    async def add(self, request: TagAddRequest) -> int:
        tag_id = await self.db.execute(
            insert(Tag).values(
                name=request.name,
                color=request.color,
                article_count=0,
            )
        )
        return tag_id

    async def update(self, request: TagUpdateRequest) -> None:
        await self._get_row(request.id)
        values: Dict[str, Any] = {}
        for key in ("name", "color"):
            val = getattr(request, key)
            if val is not None:
                values[key] = val
        throw_if(not values, ErrorCode.PARAMS_ERROR, "无更新字段")
        await self.db.execute(update(Tag).where(Tag.id == request.id).values(**values))

    async def delete(self, tag_id: int) -> None:
        await self._get_row(tag_id)
        await self.db.execute(delete(Tag).where(Tag.id == tag_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(Tag).where(Tag.id.in_(ids)))
        return result

    async def page(self, request: TagQueryRequest) -> Tuple[List[TagVO], int]:
        conditions = []
        if request.name:
            conditions.append(Tag.name.like(f"%{request.name}%"))

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(Tag.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(Tag)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(Tag.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [TagVO(**dict(r)) for r in rows]
        return records, total
