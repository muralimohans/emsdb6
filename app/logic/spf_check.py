import dns.resolver

def check_spf(email: str) -> bool:
    """Check if domain has SPF record"""
    try:
        domain = email.split("@")[1]
        answers = dns.resolver.resolve(domain, "TXT")
        for r in answers:
            if "v=spf1" in str(r):
                return True
        return False
    except Exception:
        return False
