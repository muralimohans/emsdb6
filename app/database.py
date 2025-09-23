import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

DATABASE_URL = os.environ.get("DATABASE_URL")  # provided by Render
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------
# Base class for models
# -----------------------------
Base = declarative_base()

# -----------------------------
# Async session factory
# -----------------------------
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# -----------------------------
# FastAPI dependency
# -----------------------------
async def get_db() -> AsyncSession:
    """
    Async session dependency for FastAPI routes
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with async_session() as session:
        yield session




