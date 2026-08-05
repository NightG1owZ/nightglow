from datetime import datetime
from typing import Tuple, List, Any, Dict, Optional

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.article import Article
from app.models.article_tag import ArticleTag
from app.models.article_view import ArticleView
from app.schemas.article import (
    ArticleAddRequest, ArticleUpdateRequest, ArticleQueryRequest, ArticleVO,
)


class ArticleService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, article_id: int):
        row = await self.db.fetch_one(select(Article).where(Article.id == article_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "文章不存在")
        return row

    async def get(self, article_id: int) -> ArticleVO:
        row = await self._get_row(article_id)
        return ArticleVO(**dict(row))

    async def record_view(self, article_id: int, ip: Optional[str], user_agent: Optional[str]) -> None:
        """记录浏览并使浏览量 +1"""
        await self.db.execute(
            insert(ArticleView).values(article_id=article_id, ip=ip, user_agent=user_agent)
        )
        await self.db.execute(
            update(Article).where(Article.id == article_id).values(view_count=Article.view_count + 1)
        )

    async def add(self, request: ArticleAddRequest, author_id: int) -> int:
        publish_time = request.publish_time
        if request.status == 1 and publish_time is None:
            publish_time = datetime.now()
        article_id = await self.db.execute(
            insert(Article).values(
                title=request.title,
                summary=request.summary,
                cover=request.cover,
                content=request.content,
                category_id=request.category_id,
                author_id=author_id,
                status=request.status,
                is_top=request.is_top,
                is_original=request.is_original,
                publish_time=publish_time,
            )
        )
        if request.tag_ids:
            await self.db.execute(delete(ArticleTag).where(ArticleTag.article_id == article_id))
            for tag_id in request.tag_ids:
                await self.db.execute(
                    insert(ArticleTag).values(article_id=article_id, tag_id=tag_id)
                )
        return article_id

    async def update(self, request: ArticleUpdateRequest) -> None:
        row = await self._get_row(request.id)
        existing = dict(row)
        values: Dict[str, Any] = {}
        for key in ("title", "summary", "cover", "content", "category_id", "status", "is_top", "is_original", "publish_time"):
            val = getattr(request, key)
            if val is not None:
                values[key] = val
        if "status" in values and values["status"] == 1 and "publish_time" not in values and existing.get("publish_time") is None:
            values["publish_time"] = datetime.now()
        throw_if(not values and request.tag_ids is None, ErrorCode.PARAMS_ERROR, "无更新字段")
        if values:
            await self.db.execute(update(Article).where(Article.id == request.id).values(**values))
        if request.tag_ids is not None:
            await self.db.execute(delete(ArticleTag).where(ArticleTag.article_id == request.id))
            for tag_id in request.tag_ids:
                await self.db.execute(
                    insert(ArticleTag).values(article_id=request.id, tag_id=tag_id)
                )

    async def delete(self, article_id: int) -> None:
        await self._get_row(article_id)
        await self.db.execute(delete(Article).where(Article.id == article_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(Article).where(Article.id.in_(ids)))
        return result

    async def page(self, request: ArticleQueryRequest) -> Tuple[List[ArticleVO], int]:
        conditions = []
        if request.title:
            conditions.append(Article.title.like(f"%{request.title}%"))
        if request.category_id is not None:
            conditions.append(Article.category_id == request.category_id)
        if request.status is not None:
            conditions.append(Article.status == request.status)
        if request.is_top is not None:
            conditions.append(Article.is_top == request.is_top)

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(Article.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(Article)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(Article.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [ArticleVO(**dict(r)) for r in rows]
        return records, total
