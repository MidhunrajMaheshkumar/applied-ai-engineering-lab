from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# 1. Connection Pool & Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True if you want raw SQL queries logged to stdout
    pool_size=10,
    max_overflow=20,
)

# 2. Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# 3. Base Class for ORM Models
class Base(DeclarativeBase):
    pass


# 4. Dependency Injection for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()