import pytest
import uuid
from httpx import AsyncClient
from src.logistics.models.product import Product
from src.logistics.schemas.enums import OrderStatus  # <--- Import Enum

@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient, db_session):
    """Test successful order creation."""
    # 1. Setup
    product = Product(name="Test Phone", price=1000.00, stock_quantity=10)
    db_session.add(product)
    await db_session.flush() 
    await db_session.refresh(product)

    # 2. Action
    order_data = {
        "items": [
            {"product_id": str(product.id), "quantity": 2}
        ]
    }
    response = await client.post("/api/v1/orders/", json=order_data)

    assert response.status_code == 201 
    data = response.json()

    assert data["status"] == OrderStatus.PENDING 
    assert len(data["items"]) == 1
    assert float(data["items"][0]["price_at_order"]) == 1000.00

    # 3. Verification
    await db_session.refresh(product)
    assert product.stock_quantity == 8

@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client: AsyncClient, db_session):
    """Test order failure due to insufficient stock."""
    # 1. Setup
    product = Product(name="Limited Item", price=50.00, stock_quantity=1)
    db_session.add(product)
    await db_session.flush()
    await db_session.refresh(product)

    # 2. Action
    order_data = {
        "items": [
            {"product_id": str(product.id), "quantity": 5}
        ]
    }
    response = await client.post("/api/v1/orders/", json=order_data)

    # 3. Assertions
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

    # 4. stock check
    await db_session.refresh(product)
    assert product.stock_quantity == 1

@pytest.mark.asyncio
async def test_create_order_product_not_found(client: AsyncClient, db_session):
    """Test error when ordering a non-existent product."""
    non_existent_id = str(uuid.uuid4())
    
    order_data = {
        "items": [
            {"product_id": non_existent_id, "quantity": 1}
        ]
    }
    response = await client.post("/api/v1/orders/", json=order_data)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()