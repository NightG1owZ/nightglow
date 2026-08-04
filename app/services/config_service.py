from typing import Optional, Tuple, List, Dict, Any

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.config import Config
from app.schemas.config import (
    ConfigAddRequest, ConfigUpdateRequest, ConfigQueryRequest, ConfigVO,
)


class ConfigService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, config_id: int):
        row = await self.db.fetch_one(select(Config).where(Config.id == config_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "配置不存在")
        return row

    async def get(self, config_id: int) -> ConfigVO:
        row = await self._get_row(config_id)
        return ConfigVO(**dict(row))

    async def get_by_key(self, config_key: str) -> Optional[ConfigVO]:
        row = await self.db.fetch_one(
            select(Config).where(Config.config_key == config_key)
        )
        return ConfigVO(**dict(row)) if row else None

    async def add(self, request: ConfigAddRequest) -> int:
        count = await self.db.fetch_val(
            select(func.count(Config.id)).where(Config.config_key == request.config_key)
        )
        throw_if(count > 0, ErrorCode.PARAMS_ERROR, "配置键已存在")

        config_id = await self.db.execute(
            insert(Config).values(
                config_key=request.config_key,
                config_value=request.config_value,
                description=request.description,
            )
        )
        return config_id

    async def update(self, request: ConfigUpdateRequest) -> None:
        await self._get_row(request.id)
        values: Dict[str, Any] = {}
        for key in ("config_value", "description"):
            val = getattr(request, key)
            if val is not None:
                values[key] = val
        throw_if(not values, ErrorCode.PARAMS_ERROR, "无更新字段")
        await self.db.execute(update(Config).where(Config.id == request.id).values(**values))

    async def delete(self, config_id: int) -> None:
        await self._get_row(config_id)
        await self.db.execute(delete(Config).where(Config.id == config_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(Config).where(Config.id.in_(ids)))
        return result

    async def page(self, request: ConfigQueryRequest) -> Tuple[List[ConfigVO], int]:
        conditions = []
        if request.config_key:
            conditions.append(Config.config_key.like(f"%{request.config_key}%"))

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(Config.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(Config)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(Config.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [ConfigVO(**dict(r)) for r in rows]
        return records, total
