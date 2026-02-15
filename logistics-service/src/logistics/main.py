# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from fastapi import FastAPI, Depends
# from sqlalchemy.exc import OperationalError
# import os
# from sqlalchemy.sql import text

# # Read database URL from environment variables
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/logistics_db")
# print(f"Using database URL: {DATABASE_URL}")

# # Create SQLAlchemy engine and session
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         print("+++++++++++++++++++")
#         try:
#           yield db
#         except OperationalError as e:
#             print('-------------------')
#             print(f"Database connection error: {str(e)}")
#             raise e
#     finally:
#         db.close()

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello, Thilina!"}

# @app.get("/logistics")
# def read_logistics():
#     return {"message": "Welcome to the Logistics Service!"}

# @app.get("/test-db")
# def test_db_connection(db: SessionLocal = Depends(get_db)):
#     try:
#         db.execute(text('SELECT 1'))
#         return {"message": "Database connection successful!"}
#     except OperationalError as e:
#         return {"message": f"Database connection failed! Error: {str(e)}"}

# # To run this app, use the command: uvicorn src.logistics.main:app --reload


from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.logistics.api.v1.product_router import router as product_router
from src.logistics.api.v1.order_router import router as order_router
from src.logistics.core.config import settings

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
    Returns a 500 Internal Server Error[cite: 40].
    """
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred. Please try again later."},
    )

# --- Router Registration ---

app.include_router(product_router, prefix=settings.API_V1_STR)
app.include_router(order_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check for Docker/Kubernetes probes."""
    return {"status": "healthy"}