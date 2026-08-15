from typing import Tuple, List, Any, Dict, Optional

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import (
    CommentAddRequest, CommentUpdateRequest, CommentQueryRequest, CommentVO,
)


class CommentService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, comment_id: int):
        row = await self.db.fetch_one(select(Comment).where(Comment.id == comment_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "评论不存在")
        return row

    async def get(self, comment_id: int) -> CommentVO:
        row = await self._get_row(comment_id)
        return CommentVO(**dict(row))

    async def add(self, request: CommentAddRequest, current_user: User, ip: Optional[str], user_agent: Optional[str]) -> int:
        comment_id = await self.db.execute(
            insert(Comment).values(
                article_id=request.article_id,
                parent_id=request.parent_id,
                nickname=current_user.nickname or current_user.username or "用户",
                email=current_user.email,
                avatar=current_user.avatar,
                content=request.content,
                ip=ip,
                user_agent=user_agent,
                status=1,
            )
        )
        return comment_id

    async def update(self, request: CommentUpdateRequest) -> None:
        await self._get_row(request.id)
        values: Dict[str, Any] = {}
        if request.status is not None:
            values["status"] = request.status
        throw_if(not values, ErrorCode.PARAMS_ERROR, "无更新字段")
        await self.db.execute(update(Comment).where(Comment.id == request.id).values(**values))

    async def delete(self, comment_id: int) -> None:
        await self._get_row(comment_id)
        await self.db.execute(delete(Comment).where(Comment.id == comment_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(Comment).where(Comment.id.in_(ids)))
        return result

    async def page(self, request: CommentQueryRequest) -> Tuple[List[CommentVO], int]:
        conditions = []
        if request.article_id is not None:
            conditions.append(Comment.article_id == request.article_id)
        if request.status is not None:
            conditions.append(Comment.status == request.status)

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(Comment.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(Comment)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(Comment.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [CommentVO(**dict(r)) for r in rows]
        return records, total
