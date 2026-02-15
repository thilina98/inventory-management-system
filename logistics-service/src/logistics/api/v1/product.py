from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.logistics.db.session import get_db
from src.logistics.services.product_service import ProductService
from src.logistics.schemas.product import ProductCreate, ProductRead

router = APIRouter(prefix="/product", tags=["Product"])

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, 
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    return await service.create_product(product_in)

@router.get("/", response_model=List[ProductRead])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    return await service.get_all_products(skip=skip, limit=limit)