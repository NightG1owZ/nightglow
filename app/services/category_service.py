from typing import Optional, Tuple, List, Any, Dict

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.category import Category
from app.schemas.category import (
    CategoryAddRequest, CategoryUpdateRequest, CategoryQueryRequest, CategoryVO,
)


class CategoryService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, category_id: int):
        row = await self.db.fetch_one(select(Category).where(Category.id == category_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "分类不存在")
        return row

    async def get(self, category_id: int) -> CategoryVO:
        row = await self._get_row(category_id)
        return CategoryVO(**dict(row))

    async def add(self, request: CategoryAddRequest) -> int:
        category_id = await self.db.execute(
            insert(Category).values(
                name=request.name,
                description=request.description,
                sort=request.sort,
                article_count=0,
            )
        )
        return category_id

    async def update(self, request: CategoryUpdateRequest) -> None:
        await self._get_row(request.id)
        values: Dict[str, Any] = {}
        for key in ("name", "description", "sort"):
            val = getattr(request, key)
            if val is not None:
                values[key] = val
        throw_if(not values, ErrorCode.PARAMS_ERROR, "无更新字段")
        await self.db.execute(update(Category).where(Category.id == request.id).values(**values))

    async def delete(self, category_id: int) -> None:
        await self._get_row(category_id)
        await self.db.execute(delete(Category).where(Category.id == category_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(Category).where(Category.id.in_(ids)))
        return result

    async def page(self, request: CategoryQueryRequest) -> Tuple[List[CategoryVO], int]:
        conditions = []
        if request.name:
            conditions.append(Category.name.like(f"%{request.name}%"))

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(Category.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(Category)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(Category.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [CategoryVO(**dict(r)) for r in rows]
        return records, total
