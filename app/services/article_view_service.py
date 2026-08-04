from typing import Tuple, List

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.article_view import ArticleView
from app.schemas.article_view import ArticleViewAddRequest, ArticleViewQueryRequest, ArticleViewVO


class ArticleViewService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, view_id: int):
        row = await self.db.fetch_one(select(ArticleView).where(ArticleView.id == view_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "文章浏览不存在")
        return row

    async def get(self, view_id: int) -> ArticleViewVO:
        row = await self._get_row(view_id)
        return ArticleViewVO(**dict(row))

    async def add(self, request: ArticleViewAddRequest) -> int:
        view_id = await self.db.execute(
            insert(ArticleView).values(
                article_id=request.article_id,
                ip=request.ip,
                user_agent=request.user_agent,
            )
        )
        return view_id

    async def delete(self, view_id: int) -> None:
        await self._get_row(view_id)
        await self.db.execute(delete(ArticleView).where(ArticleView.id == view_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(ArticleView).where(ArticleView.id.in_(ids)))
        return result

    async def page(self, request: ArticleViewQueryRequest) -> Tuple[List[ArticleViewVO], int]:
        conditions = []
        if request.article_id is not None:
            conditions.append(ArticleView.article_id == request.article_id)

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(ArticleView.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(ArticleView)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(ArticleView.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [ArticleViewVO(**dict(r)) for r in rows]
        return records, total
