from typing import List, Optional
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.logistics.models.order import Order, OrderItem
from src.logistics.models.product import Product
from src.logistics.repositories.order_repository import OrderRepository
from src.logistics.schemas.order import OrderCreate
from src.logistics.schemas.enums import OrderStatus

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderRepository(Order, db)

    async def create_order(self, order_in: OrderCreate) -> Order:
        """
        Creates an order transactionally.
        Supports nested transactions if called within an existing session context.
        """
        # Seniority Check: Handle existing transactions (e.g., from tests)
        if self.db.in_transaction():
            async with self.db.begin_nested():
                return await self._create_order_logic(order_in)
        else:
            async with self.db.begin():
                return await self._create_order_logic(order_in)

    async def _create_order_logic(self, order_in: OrderCreate) -> Order:
        """Internal logic to be run inside a transaction block."""
        # 1. Initialize Order
        new_order = Order(status=OrderStatus.PENDING)
        self.db.add(new_order)
        await self.db.flush()

        for item_in in order_in.items:
            # 2. Lock Product
            product_query = (
                select(Product)
                .where(Product.id == item_in.product_id, Product.deleted_at == None)
                .with_for_update()
            )
            result = await self.db.execute(product_query)
            product = result.scalar_one_or_none()

            # 3. Validations
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item_in.product_id} not found."
                )
            
            if product.stock_quantity < item_in.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}."
                )

            # 4. Update Stock
            product.stock_quantity -= item_in.quantity
            
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=item_in.quantity,
                price_at_order=product.price
            )
            self.db.add(order_item)

        await self.db.flush()

        return await self.repository.get_with_items(new_order.id)

    # ... keep get_order and update_status as they were ...
    async def get_order(self, order_id: int) -> Optional[Order]:
        return await self.repository.get_with_items(order_id)

    async def update_status(self, order_id: int, new_status: OrderStatus) -> Order:
        # Simplified for brevity - logic remains the same
        order = await self.repository.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == OrderStatus.CANCELLED and new_status == OrderStatus.SHIPPED:
            raise HTTPException(status_code=400, detail="Cannot ship a cancelled order.")
        
        order.status = new_status
        await self.db.commit()
        await self.db.refresh(order)
        return order