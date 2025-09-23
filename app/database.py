import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

DATABASE_URL = postgresql://ems6db_7ylj_user:0qVBn3zvhf6OzAzApNXnyGwEh4bGk2UK@dpg-d38osi63jp1c73asruhg-a.oregon-postgres.render.com/ems6db_7ylj
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



