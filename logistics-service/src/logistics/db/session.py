from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from src.logistics.core.config import settings

# Create the Async Engine
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True, # checks connection health before use
    pool_size=20,
    max_overflow=10,
)

# Create the Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False, # Essential for async: prevents attributes from expiring after commit
    autoflush=False,
)

# Dependency Injection for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide a database session for a request.
    Ensures the session is closed even if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()