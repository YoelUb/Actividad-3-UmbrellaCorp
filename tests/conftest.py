import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator
import httpx
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import app
from src.umbrella.db.database import get_session
from src.umbrella.db.models import Evento

DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(DATABASE_URL_TEST, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session")
async def test_app() -> AsyncGenerator[AsyncClient, None]:
    """
    Configura la app de FastAPI para tests.
    Crea las tablas de la BD antes de los tests y las borra después.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(test_app: AsyncClient) -> AsyncClient:
    """Proporciona el cliente HTTP asíncrono a cada test."""
    yield test_app

@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """
    Proporciona una sesión de BD de prueba limpia a cada test.
    """
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()