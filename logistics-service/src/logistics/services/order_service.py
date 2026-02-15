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
        Creates an order with transactional stock updates.
        Ensures atomicity and prevents race conditions.
        """
        async with self.db.begin():  # Start transaction block 
            new_order = Order(status=OrderStatus.PENDING)
            self.db.add(new_order)
            await self.db.flush()  # Generate Order ID for Foreign Keys

            for item_in in order_in.items:
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

                product.stock_quantity -= item_in.quantity

                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=product.id,
                    quantity=item_in.quantity,
                    price_at_order=product.price
                )
                self.db.add(order_item)

        return await self.repository.get_with_items(new_order.id)

    async def get_order(self, order_id: int) -> Optional[Order]:
        """Retrieve order details with items."""
        return await self.repository.get_with_items(order_id)

    async def update_status(self, order_id: int, new_status: OrderStatus) -> Order:
        """Updates status with state transition validation."""
        order = await self.repository.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status == OrderStatus.CANCELLED and new_status == OrderStatus.SHIPPED:
            raise HTTPException(
                status_code=400, 
                detail="Cannot ship a cancelled order."
            )

        order.status = new_status
        await self.db.commit()
        await self.db.refresh(order)
        return order