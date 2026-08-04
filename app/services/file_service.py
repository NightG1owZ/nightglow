from typing import Tuple, List, Any, Dict

from databases import Database
from sqlalchemy import select, func, and_, insert, update, delete

from app.exceptions import throw_if, ErrorCode
from app.models.file import File
from app.schemas.file import (
    FileAddRequest, FileUpdateRequest, FileQueryRequest, FileVO,
)


class FileService:
    def __init__(self, db: Database):
        self.db = db

    async def _get_row(self, file_id: int):
        row = await self.db.fetch_one(select(File).where(File.id == file_id))
        throw_if(not row, ErrorCode.NOT_FOUND_ERROR, "文件不存在")
        return row

    async def get(self, file_id: int) -> FileVO:
        row = await self._get_row(file_id)
        return FileVO(**dict(row))

    async def add(self, request: FileAddRequest, uploader_id: int) -> int:
        file_id = await self.db.execute(
            insert(File).values(
                filename=request.filename,
                url=request.url,
                size=request.size,
                type=request.type,
                uploader_id=uploader_id,
            )
        )
        return file_id

    async def update(self, request: FileUpdateRequest) -> None:
        await self._get_row(request.id)
        values: Dict[str, Any] = {}
        for key in ("filename", "url"):
            val = getattr(request, key)
            if val is not None:
                values[key] = val
        throw_if(not values, ErrorCode.PARAMS_ERROR, "无更新字段")
        await self.db.execute(update(File).where(File.id == request.id).values(**values))

    async def delete(self, file_id: int) -> None:
        await self._get_row(file_id)
        await self.db.execute(delete(File).where(File.id == file_id))

    async def batch_delete(self, ids: List[int]) -> int:
        result = await self.db.execute(delete(File).where(File.id.in_(ids)))
        return result

    async def page(self, request: FileQueryRequest) -> Tuple[List[FileVO], int]:
        conditions = []
        if request.filename:
            conditions.append(File.filename.like(f"%{request.filename}%"))
        if request.type:
            conditions.append(File.type == request.type)

        where_clause = and_(*conditions) if conditions else None

        count_query = select(func.count(File.id))
        if where_clause is not None:
            count_query = count_query.where(where_clause)
        total = await self.db.fetch_val(count_query)

        query = select(File)
        if where_clause is not None:
            query = query.where(where_clause)
        query = query.order_by(File.id.desc()).offset((request.current - 1) * request.page_size).limit(request.page_size)

        rows = await self.db.fetch_all(query)
        records = [FileVO(**dict(r)) for r in rows]
        return records, total
