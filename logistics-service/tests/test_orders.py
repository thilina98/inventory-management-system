import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.logistics.models.product import Product

@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient, db_session):
    """
    Test successful order creation:
    1. Create a product with stock.
    2. Place an order.
    3. Verify 201 status, stock reduction, and historical price capture.
    """
    # 1. Setup: Create a product
    product = Product(name="Test Phone", price=1000.00, stock_quantity=10)
    db_session.add(product)
    await db_session.commit()

    # 2. Action: Create Order
    order_data = {
        "items": [
            {"product_id": product.id, "quantity": 2}
        ]
    }
    response = await client.post("/api/v1/orders/", json=order_data)

    # 3. Assertions
    assert response.status_code == 201 
    data = response.json()
    assert data["status"] == "Pending"
    assert len(data["items"]) == 1
    assert float(data["items"][0]["price_at_order"]) == 1000.00

    # 4. Verify stock reduction in DB
    await db_session.refresh(product)
    assert product.stock_quantity == 8


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client: AsyncClient, db_session):
    """
    Test order failure due to insufficient stock:
    1. Create a product with low stock.
    2. Place an order exceeding that stock.
    3. Verify 400 status and that stock remains unchanged.
    """
    # 1. Setup
    product = Product(name="Limited Item", price=50.00, stock_quantity=1)
    db_session.add(product)
    await db_session.commit()

    # 2. Action: Order more than available
    order_data = {
        "items": [
            {"product_id": product.id, "quantity": 5}
        ]
    }
    response = await client.post("/api/v1/orders/", json=order_data)

    # 3. Assertions
    assert response.status_code == 400 [cite: 39, 40]
    assert "Insufficient stock" in response.json()["detail"]

    # 4. Verify stock was NOT reduced (Atomicity check)
    await db_session.refresh(product)
    assert product.stock_quantity == 1