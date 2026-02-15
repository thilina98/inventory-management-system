from typing import List, Optional
from uuid import UUID  # Fix: Added missing import
from sqlalchemy.ext.asyncio import AsyncSession
from src.logistics.repositories.product_repository import ProductRepository
from src.logistics.schemas.product import ProductCreate, ProductUpdate, ProductRead
from src.logistics.models.product import Product

class ProductService:
    def __init__(self, db: AsyncSession):
        self.repository = ProductRepository(Product, db)
        self.db = db

    async def create_product(self, product_in: ProductCreate) -> Product:
        """
        Creates a new product.
        Supports nested transactions if called within an existing session context.
        """
        if self.db.in_transaction():
            async with self.db.begin_nested():
                return await self._create_product_logic(product_in)
        else:
            async with self.db.begin():
                return await self._create_product_logic(product_in)

    async def _create_product_logic(self, product_in: ProductCreate) -> Product:
        """Internal logic to be run inside a transaction block."""
        product_data = product_in.model_dump()
        new_product = await self.repository.create(product_data)
        await self.db.flush() 
        await self.db.refresh(new_product)
        return new_product

    async def get_all_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Returns a paginated list of active products.
        """
        return await self.repository.list(skip=skip, limit=limit)

    async def get_product_by_id(self, product_id: UUID) -> Optional[Product]:
        """Retrieves a single product or returns None if it doesn't exist or is deleted."""
        return await self.repository.get(product_id)