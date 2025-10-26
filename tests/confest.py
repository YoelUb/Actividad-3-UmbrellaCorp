# tests/conftest.py
import asyncio
import sys  # <-- AÑADIDO
from pathlib import Path  # <-- AÑADIDO
from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# --- INYECTAR EL PYTHONPATH ---
# Esto es un "hack" para asegurar que Python encuentre la carpeta 'src'
# sin importar cómo se ejecute pytest.
# 1. Obtiene la ruta a este archivo (conftest.py)
# 2. Sube un nivel (a la carpeta 'tests')
# 3. Sube otro nivel (a la carpeta raíz del proyecto)
# 4. Añade esa carpeta raíz a la lista de sitios donde Python busca módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# --- FIN DEL HACK ---

# Ahora SÍ podemos importar desde 'src'
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

    async with AsyncClient(app=app, base_url="http://test") as client:
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