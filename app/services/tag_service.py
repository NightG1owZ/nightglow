from typing import Optional, Tuple, List, Any, Dict

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.article import Article
from app.models.article_tag import ArticleTag
from app.models.tag import Tag
from app.schemas.tag import (
    TagAddRequest, TagUpdateRequest, TagQueryRequest, TagVO, TagTreeVO, TagArticleVO,
)


class TagService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, tag_id: int):
        row = await self.db.fetch_one(select(Tag).where(Tag.id == tag_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "标签不存在")
        return row

    async def _get_all_tags(self) -> List[Dict[str, Any]]:
        rows = await self.db.fetch_all(select(Tag).order_by(Tag.level.asc(), Tag.id.asc()))
        return [dict(r) for r in rows]

    async def _check_name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        query = select(func.count(Tag.id)).where(Tag.name == name)
        if exclude_id is not None:
            query = query.where(Tag.id != exclude_id)
        return (await self.db.fetch_val(query)) > 0

    async def get(self, tag_id: int) -> TagVO:
        row = await self._get_row(tag_id)
        return TagVO(**dict(row))

    async def tree(self) -> List[TagTreeVO]:
        """返回完整的标签层级树（每个节点含直接关联的文章列表）"""
        tags = await self._get_all_tags()
        articles_by_tag = await self._get_articles_by_tag()
        children_map: Dict[int, List[dict]] = {}
        for t in tags:
            children_map.setdefault(t["parent_id"], []).append(t)

        def build(parent_id: int) -> List[TagTreeVO]:
            nodes = []
            for t in children_map.get(parent_id, []):
                tid = t["id"]
                articles = articles_by_tag.get(tid, [])
                nodes.append(TagTreeVO(
                    id=tid,
                    name=t["name"],
                    color=t["color"],
                    parent_id=t["parent_id"],
                    level=t["level"],
                    article_count=len(articles),
                    articles=articles,
                    children=build(tid),
                ))
            return nodes

        return build(0)

    async def _get_articles_by_tag(self) -> Dict[int, List[TagArticleVO]]:
        """查询每个标签直接关联的已发布文章（按发布时间倒序）"""
        query = (
            select(
                ArticleTag.tag_id,
                Article.id,
                Article.title,
                Article.summary,
                Article.cover,
                Article.publish_time,
                Article.create_time,
            )
            .select_from(ArticleTag)
            .join(Article, Article.id == ArticleTag.article_id)
            .where(Article.status == 1)
            .order_by(func.coalesce(Article.publish_time, Article.create_time).desc())
        )
        rows = await self.db.fetch_all(query)
        result: Dict[int, List[TagArticleVO]] = {}
        for r in rows:
            result.setdefault(r["tag_id"], []).append(TagArticleVO(
                id=r["id"],
                title=r["title"],
                summary=r["summary"],
                cover=r["cover"],
                publish_time=r["publish_time"],
                create_time=r["create_time"],
            ))
        return result

    async def add(self, request: TagAddRequest) -> int:
        throw_if(await self._check_name_exists(request.name), ErrorCode.PARAMS_ERROR, "标签名称已存在")

        parent_id = request.parent_id or 0
        level = 1
        if parent_id:
            parent = await self._get_row(parent_id)
            level = dict(parent)["level"] + 1

        tag_id = await self.db.execute(
            insert(Tag).values(
                name=request.name,
                color=request.color,
                parent_id=parent_id,
                level=level,
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
        if "name" in values:
            throw_if(await self._check_name_exists(values["name"], exclude_id=request.id), ErrorCode.PARAMS_ERROR, "标签名称已存在")
        throw_if(not values, ErrorCode.PARAMS_ERROR, "无更新字段")
        await self.db.execute(update(Tag).where(Tag.id == request.id).values(**values))

    async def _collect_descendant_ids(self, root_ids: List[int]) -> List[int]:
        """收集根标签及其所有子孙标签 ID（用于级联删除）"""
        children_map: Dict[int, List[int]] = {}
        for t in await self._get_all_tags():
            children_map.setdefault(t["parent_id"], []).append(t["id"])

        result: List[int] = []
        stack = list(root_ids)
        while stack:
            pid = stack.pop()
            result.append(pid)
            stack.extend(children_map.get(pid, []))
        return result

    async def delete(self, tag_id: int) -> None:
        await self._get_row(tag_id)
        ids = await self._collect_descendant_ids([tag_id])
        await self.db.execute(delete(ArticleTag).where(ArticleTag.tag_id.in_(ids)))
        await self.db.execute(delete(Tag).where(Tag.id.in_(ids)))

    async def batch_delete(self, ids: List[int]) -> int:
        all_ids = await self._collect_descendant_ids(ids)
        await self.db.execute(delete(ArticleTag).where(ArticleTag.tag_id.in_(all_ids)))
        result = await self.db.execute(delete(Tag).where(Tag.id.in_(all_ids)))
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
