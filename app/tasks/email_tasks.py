# app/tasks/email_tasks.py
import asyncio
from sqlalchemy.orm import Session
from app.services.email_validator import validate_email
from app.database import SessionLocal
from app.models.user import User
from app.celery_worker import celery_app
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.credits import deduct_credit, deduct_credit_sync
from celery import shared_task
from app.services.email_validator import validate_email  # async function

# -----------------------------
# Single email validation
# -----------------------------
@shared_task(bind=True)
def validate_single_email(self, email: str, user_id: int) -> dict:
    """
    Celery task to validate a single email.
    Deducts 1 credit (sync) and runs async validation.
    Returns result dict (not HTML).
    """
    db: Session = SessionLocal()
    try:
        # 1️⃣ Fetch user & deduct credit
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        if user.credits < 1:
            return {"error": "Not enough credits"}

        deduct_credit_sync(db, user_id, 1)

        # 2️⃣ Run async validate_email inside event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(validate_email(email, db, user_id, deep=True))
        loop.close()

        return result

    finally:
        db.close()


# -----------------------------
# Multiple email validation (small lists from form)
# -----------------------------
@celery_app.task(bind=True)
def validate_multiple_emails(self, emails: list[str], user_id: int):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    if user.credits < len(emails):
        return {"error": "Not enough credits"}

    async def run_validations():
        tasks = [validate_email(e, db, user_id, deep=True) for e in emails]
        return await asyncio.gather(*tasks)

    results = asyncio.run(run_validations())
    deduct_credit(db, user_id, len(emails))

    return {
        "validated": len(results),
        "remaining_credits": user.credits,
        "results": results
    }


# -----------------------------
# Bulk email validation (file upload)
# -----------------------------
@celery_app.task(bind=True)
def validate_bulk_emails(self, file_path: str, user_id: int):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    # Read emails from file
    with open(file_path, "r") as f:
        emails = [line.strip() for line in f if line.strip()]

    if user.credits < len(emails):
        return {"error": "Not enough credits"}

    async def run_validations():
        tasks = [validate_email(e, db, user_id, deep=True) for e in emails]
        return await asyncio.gather(*tasks)

    results = asyncio.run(run_validations())
    deduct_credit(db, user_id, len(emails))

    return {
        "validated": len(results),
        "remaining_credits": user.credits,
        "results": results
    }


# -----------------------------
# Batch email validation (for very large lists)
# -----------------------------
@celery_app.task(bind=True)
def validate_batch_emails(self, emails: list[str], user_id: int, batch_size: int = 50):
    """
    Validates emails in batches to avoid memory overload.
    """
    db: Session = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    if user.credits < len(emails):
        return {"error": "Not enough credits"}

    all_results = []

    async def run_batch(batch):
        tasks = [validate_email(e, db, user_id, deep=True) for e in batch]
        return await asyncio.gather(*tasks)

    # Process in batches
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i + batch_size]
        batch_results = asyncio.run(run_batch(batch))
        all_results.extend(batch_results)
        deduct_credit(db, user_id, len(batch))  # Deduct per batch

    return {
        "validated": len(all_results),
        "remaining_credits": user.credits,
        "results": all_results
    }
