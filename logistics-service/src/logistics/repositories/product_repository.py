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
