# app/logic/blacklist_check.py

BLACKLISTED_DOMAINS = {"spam.com", "fakeemail.com", "baddomain.org"}

def check_blacklist(email: str) -> bool:
    """
    Returns True if email is blacklisted, False otherwise.
    """
    domain = email.split("@")[-1].lower()
    return domain in BLACKLISTED_DOMAINS
