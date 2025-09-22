DISPOSABLE_DOMAINS = {
    "mailinator.com",
    "10minutemail.com",
    "tempmail.com",
}

def check_disposable(email: str) -> bool:
    """Detect if domain is in disposable list"""
    domain = email.split("@")[1]
    return domain not in DISPOSABLE_DOMAINS
