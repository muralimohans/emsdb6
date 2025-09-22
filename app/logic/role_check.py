import asyncio
import dns.resolver

ROLE_EMAILS = {
    "admin", "info", "support", "contact", "sales", "webmaster"
}

async def check_role(email: str) -> bool:
    local = email.split("@")[0].lower()
    role_accounts = ["admin", "support", "info", "sales"]
    return await asyncio.to_thread(lambda: local in role_accounts)
