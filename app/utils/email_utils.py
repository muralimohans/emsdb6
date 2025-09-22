import re
import dns.resolver

def generate_email_patterns(name: str, company: str):
    if not name or not company:
        return []

    name = name.strip().lower()
    company = company.strip().lower()

    domain = company.replace(" ", "").lower()
    if "." not in domain:
        domain += ".com"

    parts = name.split()
    first = parts[0]
    last = parts[-1] if len(parts) > 1 else ""

    patterns = []
    if first and last:
        patterns.append(f"{first}.{last}@{domain}")
        patterns.append(f"{first}{last}@{domain}")
        patterns.append(f"{first[0]}{last}@{domain}")
    if first:
        patterns.append(f"{first}@{domain}")

    return patterns


def verify_email(email: str) -> bool:
    if not email:
        return False

    email = email.strip()
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    try:
        domain = email.split("@")[1]
        dns.resolver.resolve(domain, "MX")
        return True
    except Exception:
        return False
