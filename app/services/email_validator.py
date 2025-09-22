import re
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.email_crud import save_validation_result
from app.logic.mx_check import check_mx_record
from app.logic.dns_check import check_dns_record
from app.logic.dkim_check import check_dkim
from app.logic.spf_check import check_spf
from app.logic.smtp_check import check_smtp
from app.logic.blacklist_check import check_blacklist
from app.logic.freemail_check import check_freemail
from app.logic.role_check import check_role
from app.utils.credits import deduct_credit   # ✅ Import credit utility


# Scoring weights
WEIGHTS = {
    "syntax": 20,
    "mx": 20,
    "spf": 10,
    "dkim": 10,
    "blacklist": 20,
    "catchall": -10,
    "role": -5,
    "free": -5,
    "smtp": 20,
}


def categorize_email(score: int) -> str:
    if score >= 70:
        return "valid"
    elif score >= 40:
        return "possibly valid"
    elif score >= 20:
        return "risky"
    return "invalid"


async def validate_email(email: str, db: AsyncSession, user_id: int, deep: bool = True) -> dict:
    """
    Validate a single email with scoring + category.
    Deducts 1 credit before validation.
    """
    # 🔑 Step 0 — Deduct credit (fail fast if no balance)
    await deduct_credit(db, user_id, amount=1)

    score = 0
    details = {
        "syntax": False,
        "mx": None,
        "catchall": None,
        "spf": None,
        "dkim": None,
        "smtp": None,
        "blacklist": None,
        "role": None,
        "free": None,
    }

    # 1️⃣ Syntax check
    syntax_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    syntax_ok = bool(re.match(syntax_regex, email))
    details["syntax"] = syntax_ok
    if syntax_ok:
        score += WEIGHTS.get("syntax", 0)

    if deep and syntax_ok:
        # 2️⃣ MX record check
        mx_ok = await check_mx_record(email)
        details["mx"] = mx_ok
        if mx_ok:
            score += WEIGHTS.get("mx", 0)

        # 3️⃣ DNS / catch-all check
        catchall_ok = await check_dns_record(email)
        details["catchall"] = catchall_ok
        if catchall_ok:
            score += WEIGHTS.get("catchall", 0)

        # 4️⃣ SPF
        spf_ok = check_spf(email)
        details["spf"] = spf_ok
        if spf_ok:
            score += WEIGHTS.get("spf", 0)

        # 5️⃣ DKIM
        dkim_ok = check_dkim(email)
        details["dkim"] = dkim_ok
        if dkim_ok:
            score += WEIGHTS.get("dkim", 0)

        # 6️⃣ SMTP
        smtp_ok = check_smtp(email)
        details["smtp"] = smtp_ok
        if smtp_ok:
            score += WEIGHTS.get("smtp", 0)

        # 7️⃣ Blacklist
        blacklist_ok = not check_blacklist(email)
        details["blacklist"] = blacklist_ok
        if blacklist_ok:
            score += WEIGHTS.get("blacklist", 0)

        # 8️⃣ Role-based
        role_ok = not check_role(email)
        details["role"] = role_ok
        if role_ok:
            score += WEIGHTS.get("role", 0)

        # 9️⃣ Free email
        free_ok = not check_freemail(email)
        details["free"] = free_ok
        if free_ok:
            score += WEIGHTS.get("free", 0)

    # 🔟 Compute category/status
    status = categorize_email(score)

    # ✅ Save result to DB
    await save_validation_result(
        db=db,
        email=email,
        valid_syntax=details["syntax"],
        domain_exists=details["catchall"],
        mx_exists=details["mx"],
        smtp_ok=details["smtp"],
        status=status,
        score=score,
        user_id=user_id,
    )

    # ✅ Return for API/template
    return {
        "email": email,
        "score": score,
        "status": status,
        "category": status,
        "details": details,
    }
