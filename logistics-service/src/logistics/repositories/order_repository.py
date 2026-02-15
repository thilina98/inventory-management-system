from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.logistics.models.order import Order, OrderItem
from src.logistics.repositories.base import BaseRepository
from uuid import UUID

class OrderRepository(BaseRepository[Order]):
    async def get_with_items(self, order_id: UUID) -> Optional[Order]:
        """
        Retrieves an order with all its items eagerly loaded in a single logical operation.
        Using selectinload is the industry standard for high-throughput async loading
        of one-to-many relationships.
        """
        query = (
            select(self.model)
            .options(selectinload(self.model.items))
            .where(
                self.model.id == order_id,
                self.model.deleted_at == None
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def list_with_items(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Lists orders with items eagerly loaded, applying pagination and soft-delete filters.
        """
        query = (
            select(self.model)
            .options(selectinload(self.model.items))
            .where(self.model.deleted_at == None)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    def add_order_item(self, order_item: OrderItem) -> None:
        """
        Helper to add an item to the session.
        The actual transactional logic and stock validation will occur in the Service layer.
        """
        self.db_session.add(order_item)