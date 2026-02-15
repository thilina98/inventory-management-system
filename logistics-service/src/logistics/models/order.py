from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.logistics.db.base import Base
from src.logistics.schemas.enums import OrderStatus # Reusing the domain Enum

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    status = Column(
        SQLEnum(OrderStatus),
        nullable=False, 
        default=OrderStatus.PENDING, 
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship for Eager Loading
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Numeric(10, 2), nullable=False) # Historical integrity 

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")