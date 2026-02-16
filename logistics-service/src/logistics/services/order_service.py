from typing import List, Optional
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.logistics.models.order import Order, OrderItem
from src.logistics.models.product import Product
from src.logistics.repositories.order_repository import OrderRepository
from src.logistics.repositories.product_repository import ProductRepository
from src.logistics.schemas.order import OrderCreate
from src.logistics.schemas.enums import OrderStatus

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = OrderRepository(Order, db)
        self.product_repository = ProductRepository(Product, db)

    async def create_order(self, order_in: OrderCreate) -> Order:
        """
        Creates an order transactionally.
        Supports nested transactions if called within an existing session context.
        """
        if self.db.in_transaction():
            async with self.db.begin_nested():
                return await self._create_order_logic(order_in)
        else:
            async with self.db.begin():
                return await self._create_order_logic(order_in)

    async def _create_order_logic(self, order_in: OrderCreate) -> Order:
        """Internal logic to be run inside a transaction block."""
        # Initialize Order
        new_order = Order(status=OrderStatus.PENDING)
        self.db.add(new_order)
        await self.db.flush()

        # sort prdduct IDs to prevent deadlocks
        item_map = {item.product_id: item.quantity for item in order_in.items}
        sorted_product_ids = sorted(item_map.keys())

        # Batch Fetch & Lock (for N+1 Problem)
        products = await self.product_repository.get_many_for_update(sorted_product_ids)

        if len(products) != len(sorted_product_ids):
            found_ids = {p.id for p in products}
            missing_ids = set(sorted_product_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Products not found: {missing_ids}"
            )

        for product in products:
            qty_needed = item_map[product.id]

            if product.stock_quantity < qty_needed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}"
                )

            product.stock_quantity -= qty_needed

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=qty_needed,
                price_at_order=product.price
            )
            self.db.add(order_item)

        await self.db.flush()
        return await self.repository.get_with_items(new_order.id)

    async def get_order(self, order_id: int) -> Optional[Order]:
        return await self.repository.get_with_items(order_id)

    async def update_status(self, order_id: int, new_status: OrderStatus) -> Order:
        order = await self.repository.get(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == OrderStatus.CANCELLED and new_status == OrderStatus.SHIPPED:
            raise HTTPException(status_code=400, detail="Cannot ship a cancelled order.")
        
        order.status = new_status
        await self.db.commit()
        await self.db.refresh(order)
        return order