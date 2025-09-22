# app/logic/mx_check.py
import asyncio
import dns.resolver

async def check_mx_record(email: str) -> bool:
    """Check MX record (async-safe)."""
    domain = email.split("@")[-1]
    try:
        return await asyncio.to_thread(
            lambda: bool(dns.resolver.resolve(domain, "MX"))
        )
    except Exception:
        return False
