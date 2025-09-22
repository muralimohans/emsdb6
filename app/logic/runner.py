from app.logic.category_mapper import map_score_to_category
from app.logic.syntax_check import check_syntax
from app.logic.domain_check import check_domain
from app.logic.catchall_check import check_catchall
from app.logic.freemail_check import check_freemail
from app.logic.spf_check import check_spf
from app.logic.dkim_check import check_dkim
from app.logic.dmarc_check import check_dmarc
from app.logic.smtp_check import check_smtp
from app.logic.role_check import check_role
from app.logic.blacklist_check import check_blacklist
from app.logic.greylist_check import check_greylist
from app.logic.domain_expiry_check import check_domain_expiry
from app.logic.alias_forward_check import check_alias_forward_check
import dns.resolver

def run_validations(email: str, deep: bool = False) -> dict:
    """
    Run full professional-grade validations and compute a score (0-100)
    """
    report = {}
    score = 100

    # Basic checks
    report["syntax"] = check_syntax(email)
    if not report["syntax"]:
        score = 0
        report["status"] = "invalid_syntax"
        return {**report, "score": score}

    report["domain"] = check_domain(email)
    if not report["domain"]:
        score = 0
        report["status"] = "invalid_domain"
        return {**report, "score": score}

    report["domain_active"] = check_domain_expiry(email)
    if not report["domain_active"]:
        score -= 30

    report["blacklisted"] = check_blacklist(email)
    if report["blacklisted"]:
        score = 0
        report["status"] = "blacklisted"
        return {**report, "score": score}

    # Optional risk factors
    report["freemail"] = check_freemail(email)
    report["role_based"] = check_role(email)
    report["alias_forward"] = check_alias_forward_check(email)
    for check, deduction in [("freemail", 10), ("role_based", 15), ("alias_forward", 10)]:
        if report[check]:
            score -= deduction

    # Authentication checks
    report["spf"] = check_spf(email)
    report["dkim"] = check_dkim(email)
    report["dmarc"] = check_dmarc(email)
    for check in ["spf", "dkim", "dmarc"]:
        if not report[check]:
            score -= 5

    # Deep checks
    if deep:
        report["catchall"] = check_catchall(email)
        try:
            mx_records = dns.resolver.resolve(email.split("@")[1], "MX")
            mx_host = str(mx_records[0].exchange)
            report["smtp"] = check_smtp(email)
            report["greylist_retry"] = check_greylist(email, mx_host)
            if not report["smtp"] or not report["greylist_retry"]:
                score -= 20
        except Exception:
            report["smtp"] = False
            report["greylist_retry"] = False
            score -= 20
    else:
        report["catchall"] = None
        report["smtp"] = None
        report["greylist_retry"] = None

    # Cap score between 0 and 100
    score = max(0, min(100, score))

    # Determine final status based on score
    if score >= 90:
        report["status"] = "valid"
    elif score >= 70:
        report["status"] = "risky"
    elif score >= 50:
        report["status"] = "possibly_invalid"
    else:
        report["status"] = "invalid"

    # Map score to category
    category = map_score_to_category(score)
    report["status"] = category
    report["score"] = score
    return report
