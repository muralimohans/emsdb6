import re
from app.services.validation_checks import (
    check_mx_record,
    check_smtp,
    check_spf,
    check_dkim,
    check_blacklist,
    check_role,
    check_freemail,
    check_dns_record
)
from app.crud.email_crud import save_validation_result

# Define your scoring weights
WEIGHTS = {
    "syntax": 20,
    "mx": 20,
    "spf": 10,
    "dkim": 10,
    "smtp": 20,
    "blacklist": 20,
    "catchall": -10,
    "role": -5,
    "free": -5
}

def categorize_email(score: int) -> str:
    if score >= 80:
        return "valid"
    elif score >= 50:
        return "possibly valid"
    else:
        return "risky"

async def validate_email(email: str, db, user_id: int, deep: bool = True) -> dict:
    """
    Full async email validation returning detailed results.
    deep=True → run MX, SMTP, SPF, DKIM, blacklist, role, free email checks
    """
    score = 0
    details = {}

    # 1️⃣ Syntax check
    syntax_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    syntax_ok = bool(re.match(syntax_regex, email))
    details["syntax"] = syntax_ok
    if syntax_ok:
        score += WEIGHTS["syntax"]

    local_part, domain = email.split("@") if "@" in email else (email, "")
    details["local_part"] = local_part
    details["domain"] = domain.lower()
    domain_exists = False

    if deep:
        # 2️⃣ Domain / MX check
        domain_exists = await check_dns_record(domain)
        mx_ok = await check_mx_record(domain)
        details["domain_exists"] = domain_exists
        details["mx"] = mx_ok
        if domain_exists:
            score += WEIGHTS["mx"]

        # 3️⃣ SPF check
        spf_ok = await check_spf(domain)
        details["spf"] = spf_ok
        if spf_ok:
            score += WEIGHTS["spf"]

        # 4️⃣ DKIM check
        dkim_ok = await check_dkim(domain)
        details["dkim"] = dkim_ok
        if dkim_ok:
            score += WEIGHTS["dkim"]

        # 5️⃣ SMTP check
        smtp_ok = await check_smtp(email)
        details["smtp"] = smtp_ok
        if smtp_ok:
            score += WEIGHTS["smtp"]

        # 6️⃣ Blacklist check
        blacklist_ok = not await check_blacklist(email)
        details["blacklist"] = blacklist_ok
        if blacklist_ok:
            score += WEIGHTS["blacklist"]

        # 7️⃣ Role-based penalty
        role_ok = not await check_role(email)
        details["role"] = role_ok
        if role_ok:
            score += WEIGHTS["role"]

        # 8️⃣ Free email penalty
        free_ok = not await check_freemail(email)
        details["free"] = free_ok
        if free_ok:
            score += WEIGHTS["free"]

        # 9️⃣ Catch-all penalty
        catchall_ok = not await check_smtp(email, check_catchall=True)
        details["catchall"] = catchall_ok
        if catchall_ok:
            score += WEIGHTS["catchall"]

    # Compute status
    if score >= 80:
        status = "valid"
    elif score >= 50:
        status = "possibly valid"
    else:
        status = "risky"

    # Save to DB
    await save_validation_result(
        db=db,
        email=email,
        valid_syntax=syntax_ok,
        domain_exists=domain_exists,
        mx_exists=details.get("mx", False),
        smtp_ok=details.get("smtp", False),
        status=status,
        score=score,
        user_id=user_id
    )

    return {
        "email": email,
        "local_part": local_part,
        "domain": domain.lower(),
        "score": score,
        "status": status,
        "details": details
    }
