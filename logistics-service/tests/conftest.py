import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.logistics.main import app
from src.logistics.db.base import Base
from src.logistics.db.session import get_db
from src.logistics.core.config import settings

@pytest.fixture(scope="session")
async def db_engine():
    """
    Creates the async engine within the correct event loop context.
    Scope='session' ensures we reuse the connection pool across tests.
    """
    engine = create_async_engine(str(settings.SQLALCHEMY_TEST_DATABASE_URI), pool_pre_ping=True)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session")
async def db_session_factory(db_engine):
    """
    Creates the session factory bound to the session-scoped engine.
    """
    return async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def setup_db(db_engine):
    """
    Initialize the test database schema.
    Runs once per session.
    """
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(db_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a clean database session for each test.
    Rolls back transaction after yield to ensure test isolation.
    """
    async with db_session_factory() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an AsyncClient for FastAPI.
    Overrides the get_db dependency to use the test session.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()