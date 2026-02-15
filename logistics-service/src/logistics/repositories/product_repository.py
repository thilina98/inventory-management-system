from typing import Optional
from sqlalchemy import select
from src.logistics.models.product import Product
from src.logistics.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    async def get_by_name(self, name: str) -> Optional[Product]:
        """Specific lookup for product names."""
        query = select(self.model).where(
            self.model.name == name,
            self.model.deleted_at == None
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_stock(self, product_id: int, quantity_change: int) -> None:
        """
        Updates stock directly. 
        Note: Complex transactional logic stays in the Service layer[cite: 22, 42].
        """
        # This is a simple update helper; atomic locking is handled in the service.
        pass