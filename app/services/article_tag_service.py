from typing import Tuple, List

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.article_tag import ArticleTag
from app.schemas.article_tag import ArticleTagAddRequest, ArticleTagQueryRequest, ArticleTagVO


class ArticleTagService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, article_tag_id: int):
        row = await self.db.fetch_one(select(ArticleTag).where(ArticleTag.id == article_tag_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "文章标签关联不存在")
        return row

    async def get(self, article_tag_id: int) -> ArticleTagVO:
        row = await self._get_row(article_tag_id)
        return ArticleTagVO(**dict(row))

    async def add(self, request: ArticleTagAddRequest) -> int:
        article_tag_id = await self.db.execute(
            insert(ArticleTag).values(
                article_id=request.article_id,
                tag_id=request.tag_id,
            )
        )
        return article_tag_id

    async def delete(self, article_tag_id: int) -> None:
        await self._get_row(article_tag_id)
        await self.db.execute(delete(ArticleTag).where(ArticleTag.id == article_tag_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(ArticleTag).where(ArticleTag.id.in_(ids)))
        return result

    async def page(self, request: ArticleTagQueryRequest) -> Tuple[List[ArticleTagVO], int]:
        conditions = []
        if request.article_id is not None:
            conditions.append(ArticleTag.article_id == request.article_id)
        if request.tag_id is not None:
            conditions.append(ArticleTag.tag_id == request.tag_id)

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(ArticleTag.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(ArticleTag)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(ArticleTag.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [ArticleTagVO(**dict(r)) for r in rows]
        return records, total
