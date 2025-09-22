import whois

def check_domain_expiry(email: str) -> bool:
    """Check if the domain is active (not expired)"""
    try:
        domain = email.split("@")[1]
        w = whois.whois(domain)
        return w.expiration_date is not None
    except Exception:
        return False
