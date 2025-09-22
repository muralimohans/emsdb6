from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# -----------------------------
# Database URL
# -----------------------------
DATABASE_URL = settings.database_url  # e.g., "postgresql+asyncpg://user:password@db:5432/ems6db"

# -----------------------------
# Async Engine
# -----------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

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

# Optional: synchronous session factory (rarely needed with FastAPI async)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession  # only use if really needed
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
