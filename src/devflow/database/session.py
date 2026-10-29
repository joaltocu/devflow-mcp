"""Database session management."""

import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from devflow.database.models import Base

# Create .devflow directory in user's home
DEVFLOW_DIR = Path.home() / ".devflow"
DEVFLOW_DIR.mkdir(exist_ok=True)

# Default database location: ~/.devflow/devflow.db
DEFAULT_DB_PATH = DEVFLOW_DIR / "devflow.db"

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DEVFLOW_DATABASE_URL",
    f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}",
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_pre_ping=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database (create tables)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session.

    Usage:
        async with get_session() as session:
            # Use session
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
