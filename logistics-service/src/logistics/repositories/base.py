from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.logistics.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get(self, id: Any) -> Optional[ModelType]:
        """Fetch a single record by ID, excluding soft-deleted ones."""
        query = select(self.model).where(
            self.model.id == id,
            self.model.deleted_at == None
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List records with pagination"""
        query = (
            select(self.model)
            .where(self.model.deleted_at == None)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in_data: dict) -> ModelType:
        """Create a new database record."""
        db_obj = self.model(**obj_in_data)
        self.db_session.add(db_obj)
        # No commit here; the Service layer manages the transaction boundary
        return db_obj