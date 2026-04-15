from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Float,
    ForeignKey,
    Text,
    Index,
    JSON,
)

DB_URI = "postgresql+asyncpg://postgres:postgres@localhost:5432/api_key_authorization"

engine = create_async_engine(
    url=DB_URI,
    echo=True,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=60,
    pool_pre_ping=True,
    pool_recycle=3600,
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        raise

class Key(Base):
    __tablename__ = "api_key"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String)
    key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    
