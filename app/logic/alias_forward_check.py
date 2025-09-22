
async def check_alias_forward_check(email: str) -> bool:
    """
    Detect plus-addressing and common forwarding patterns.
    Example: user+news@gmail.com → alias forwarding
    """
    local_part = email.split("@")[0]
    return "+" in local_part or local_part.startswith("forward")
