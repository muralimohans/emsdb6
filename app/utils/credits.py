from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.user import User


# ---------- Async Utilities ----------

async def deduct_credit(db: AsyncSession, user_id: int, amount: int = 1) -> None:
    """
    Deduct credits from a user (async version).
    Raises HTTPException if user not found or insufficient credits.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.credits < amount:
        raise HTTPException(status_code=400, detail="Not enough credits")

    user.credits -= amount
    await db.commit()
    await db.refresh(user)


async def add_credit(db: AsyncSession, user_id: int, amount: int = 1) -> None:
    """
    Add credits to a user (async version).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.credits += amount
    await db.commit()
    await db.refresh(user)


async def get_credits(db: AsyncSession, user_id: int) -> int:
    """
    Get current credit balance (async version).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.credits


# ---------- Sync Utilities (for Celery tasks) ----------

def deduct_credit_sync(db: Session, user_id: int, amount: int = 1) -> None:
    """
    Deduct credits from a user (sync version).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.credits < amount:
        raise HTTPException(status_code=400, detail="Not enough credits")

    user.credits -= amount
    db.commit()
    db.refresh(user)


def add_credit_sync(db: Session, user_id: int, amount: int = 1) -> None:
    """
    Add credits to a user (sync version).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.credits += amount
    db.commit()
    db.refresh(user)


def get_credits_sync(db: Session, user_id: int) -> int:
    """
    Get current credit balance (sync version).
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.credits
