from typing import Optional
from sqlalchemy import select
from src.logistics.models.product import Product
from src.logistics.repositories.base import BaseRepository
from uuid import UUID

class ProductRepository(BaseRepository[Product]):
    async def get_by_name(self, name: str) -> Optional[Product]:
        """Specific lookup for product names."""
        query = select(self.model).where(
            self.model.name == name,
            self.model.deleted_at == None
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_many_for_update(self, product_ids: list[UUID]) -> list[Product]:
        query = (
            select(self.model)
            .where(self.model.id.in_(product_ids))
            .where(self.model.deleted_at == None)
            .with_for_update()
        )
        result = await self.db_session.execute(query)
        return result.scalars().all()
