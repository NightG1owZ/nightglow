from typing import Tuple, List, Optional

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.article import Article
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

    async def add(self, request: ArticleLikeAddRequest, ip: Optional[str], user_id: Optional[int]) -> int:
        # 基于 IP 去重：同一 IP 对同一文章仅可点赞一次
        count = await self.db.fetch_val(
            select(func.count(ArticleLike.id)).where(
                and_(ArticleLike.article_id == request.article_id, ArticleLike.ip == ip)
            )
        )
        throw_if(count > 0, ErrorCode.OPERATION_ERROR, "已点赞过该文章")

        like_id = await self.db.execute(
            insert(ArticleLike).values(
                article_id=request.article_id,
                ip=ip,
                user_id=user_id,
            )
        )
        # 点赞数 +1
        await self.db.execute(
            update(Article).where(Article.id == request.article_id).values(like_count=Article.like_count + 1)
        )
        return like_id

    async def cancel(self, article_id: int, ip: Optional[str]) -> bool:
        """按 article_id + IP 取消点赞，点赞数 -1"""
        row = await self.db.fetch_one(
            select(ArticleLike).where(
                and_(ArticleLike.article_id == article_id, ArticleLike.ip == ip)
            )
        )
        if not row:
            return False
        await self.db.execute(delete(ArticleLike).where(ArticleLike.id == row.id))
        await self.db.execute(
            update(Article).where(Article.id == article_id).values(like_count=Article.like_count - 1)
        )
        return True

    async def delete(self, like_id: int) -> None:
        row = await self._get_row(like_id)
        await self.db.execute(delete(ArticleLike).where(ArticleLike.id == like_id))
        # 点赞数 -1
        await self.db.execute(
            update(Article).where(Article.id == row.article_id).values(like_count=Article.like_count - 1)
        )

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
