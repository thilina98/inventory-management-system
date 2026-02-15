from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from src.logistics.schemas.enums import OrderStatus
from uuid import UUID

# --- Order Item Schemas ---

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0, description="Quantity must be at least 1")

# Input: User only provides product and quantity
class OrderItemCreate(OrderItemBase):
    pass

# Output: We return everything, including the historical price
class OrderItemRead(OrderItemBase):
    id: UUID
    price_at_order: Decimal

    model_config = ConfigDict(from_attributes=True)


# --- Order Schemas ---

class OrderBase(BaseModel):
    pass

# Input: User sends a list of items to order
class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Order must contain at least one item")

# Output: Full order details with nested items
class OrderRead(OrderBase):
    id: UUID
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemRead] # Nested schema for eager loading display

    model_config = ConfigDict(from_attributes=True)

class OrderUpdateStatus(BaseModel):
    status: OrderStatus
