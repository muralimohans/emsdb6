from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.email import EmailValidation


async def save_validation_result(
    db: AsyncSession,
    email: str,
    valid_syntax: bool,
    domain_exists: bool,
    mx_exists: bool,
    smtp_ok: bool,
    status: str,
    score: int,
    user_id: int,
):
    """Save or update validation result in DB"""
    # 🔍 check if record already exists
    result = await db.execute(
        select(EmailValidation).where(EmailValidation.email == email, EmailValidation.user_id == user_id)
    )
    record = result.scalar_one_or_none()

    if record:
        # update existing record
        record.valid_syntax = valid_syntax
        record.domain_exists = domain_exists
        record.mx_exists = mx_exists
        record.smtp_ok = smtp_ok
        record.status = status
        record.score = score
    else:
        # create new record
        record = EmailValidation(
            user_id=user_id,
            email=email,
            valid_syntax=valid_syntax,
            domain_exists=domain_exists,
            mx_exists=mx_exists,
            smtp_ok=smtp_ok,
            status=status,
            score=score,
        )
        db.add(record)

    await db.commit()
    await db.refresh(record)
    return record

# existing async save_validation_result remains untouched

def save_validation_result_sync(db, email: str, valid_syntax: bool, domain_exists: bool,
                                mx_exists: bool, smtp_ok: bool, status: str,
                                score: int, user_id: int) -> None:
    from app.models.email_result import EmailResult

    result = EmailResult(
        email=email,
        valid_syntax=valid_syntax,
        domain_exists=domain_exists,
        mx_exists=mx_exists,
        smtp_ok=smtp_ok,
        status=status,
        score=score,
        user_id=user_id,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
