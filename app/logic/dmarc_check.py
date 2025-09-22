import dns.resolver

def check_dmarc(email: str) -> bool:
    """Check for DMARC record"""
    try:
        domain = email.split("@")[1]
        record = f"_dmarc.{domain}"
        answers = dns.resolver.resolve(record, "TXT")
        return len(answers) > 0
    except Exception:
        return False
