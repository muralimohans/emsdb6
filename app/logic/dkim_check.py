import dns.resolver

def check_dkim(email: str) -> bool:
    """Check for DKIM record (selector default: 'default._domainkey')"""
    try:
        domain = email.split("@")[1]
        selector = "default"
        record = f"{selector}._domainkey.{domain}"
        answers = dns.resolver.resolve(record, "TXT")
        return len(answers) > 0
    except Exception:
        return False
