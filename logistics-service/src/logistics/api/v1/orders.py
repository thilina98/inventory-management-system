from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.logistics.db.session import get_db
from src.logistics.services.order_service import OrderService
from src.logistics.schemas.order import OrderCreate, OrderRead, OrderUpdateStatus
from src.logistics.schemas.enums import OrderStatus

router = APIRouter(prefix="/orders", tags=["Order"])

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Critical Logic: Creates an order transactionally, checking and reducing stock.
    Handles insufficient stock error with proper HTTP codes[cite: 22, 39].
    """
    service = OrderService(db)
    return await service.create_order(order_in)

@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves order details including nested items.
    """
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.patch("/{order_id}/status", response_model=OrderRead)
async def update_order_status(
    order_id: int,
    status_update: OrderUpdateStatus,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates an order's status with transition validation.
    """
    service = OrderService(db)
    return await service.update_status(order_id, status_update.status)