import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel


load_dotenv()
Database_url = os.getenv("DATABASE_URL")

if not Database_url:
    raise Exception("Dont find the DATABASE_URL env variable")

engine = create_async_engine(Database_url, echo=True)


async def create_db_and_tables():

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación y creando tablas...")
    await create_db_and_tables()
    print("Tablas creadas. Aplicación lista.")
    yield


async def get_session():
    async with AsyncSession(engine) as session:
        yield session

session_dep = Annotated[AsyncSession, Depends(get_session)]