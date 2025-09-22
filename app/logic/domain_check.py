import dns.resolver

def check_domain(email: str) -> bool:
    """Check if domain exists and has MX records"""
    try:
        domain = email.split("@")[1]
        answers = dns.resolver.resolve(domain, "MX")
        return len(answers) > 0
    except Exception:
        return False
