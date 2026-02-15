from typing import List, Optional
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
        Validation of non-negative stock and price is handled by the Pydantic schema.
        """
        product_data = product_in.model_dump()
        new_product = await self.repository.create(product_data)
        await self.db.commit()
        await self.db.refresh(new_product)
        return new_product

    async def get_all_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Returns a paginated list of active products.
        Soft-deleted products are filtered out at the repository level.
        """
        return await self.repository.list(skip=skip, limit=limit)

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Retrieves a single product or returns None if it doesn't exist or is deleted."""
        return await self.repository.get(product_id)