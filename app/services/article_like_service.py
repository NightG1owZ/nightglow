from typing import Tuple, List

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.article_like import ArticleLike
from app.schemas.article_like import ArticleLikeAddRequest, ArticleLikeQueryRequest, ArticleLikeVO


class ArticleLikeService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, like_id: int):
        row = await self.db.fetch_one(select(ArticleLike).where(ArticleLike.id == like_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "文章点赞不存在")
        return row

    async def get(self, like_id: int) -> ArticleLikeVO:
        row = await self._get_row(like_id)
        return ArticleLikeVO(**dict(row))

    async def add(self, request: ArticleLikeAddRequest) -> int:
        like_id = await self.db.execute(
            insert(ArticleLike).values(
                article_id=request.article_id,
                ip=request.ip,
                user_id=request.user_id,
            )
        )
        return like_id

    async def delete(self, like_id: int) -> None:
        await self._get_row(like_id)
        await self.db.execute(delete(ArticleLike).where(ArticleLike.id == like_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(ArticleLike).where(ArticleLike.id.in_(ids)))
        return result

    async def page(self, request: ArticleLikeQueryRequest) -> Tuple[List[ArticleLikeVO], int]:
        conditions = []
        if request.article_id is not None:
            conditions.append(ArticleLike.article_id == request.article_id)
        if request.user_id is not None:
            conditions.append(ArticleLike.user_id == request.user_id)

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(ArticleLike.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(ArticleLike)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(ArticleLike.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [ArticleLikeVO(**dict(r)) for r in rows]
        return records, total
