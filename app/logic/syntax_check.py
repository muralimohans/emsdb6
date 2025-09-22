import re

def check_syntax(email: str) -> bool:
    """Validate email syntax using regex"""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None
