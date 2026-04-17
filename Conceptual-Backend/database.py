from typing import AsyncIterator
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DB_URI = os.getenv("POSTGRES_URI")

logger.debug(f"Configuring database engine with pool_size=5, max_overflow=10, pool_timeout=60")
logger.debug(f"Database URI configured (masked for security)")

engine = create_async_engine(
    url=DB_URI,
    echo=False,
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
        logger.info("Starting database table initialization")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created or verified successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {str(e)}", exc_info=True)
        raise