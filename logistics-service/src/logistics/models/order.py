from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from src.logistics.db.base import Base
from src.logistics.schemas.enums import OrderStatus # Reusing the domain Enum

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # Using the Enum type for database-level validation 
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships: Eager loading capability [cite: 37, 38]
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_order = Column(Numeric(10, 2), nullable=False) # Historical integrity 

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product") # Links OrderItem to Product