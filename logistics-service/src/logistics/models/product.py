from sqlalchemy import Column, Integer, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.logistics.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), nullable=False, index=True) # Indexed for high-throughput searching 
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)

    # Metadata for auditing and Soft Delete
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint('stock_quantity >= 0', name='check_stock_non_negative'),
    )