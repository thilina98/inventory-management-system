from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import logging

from src.logistics.api.v1.products import router as products
from src.logistics.api.v1.orders import router as orders
from src.logistics.core.config import settings
from src.logistics.db.session import get_db

# Setup logging for production monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- Global Exception Handlers ---

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Catch-all for database errors to prevent leaking internal DB details.
    """
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )

# --- Router Registration ---

app.include_router(products, prefix=settings.API_V1_STR)
app.include_router(orders, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            # content={"status": "unhealthy", "detail": "Database connection failed"}
            content={"status": "unhealthy", "detail": str(e)}
        )