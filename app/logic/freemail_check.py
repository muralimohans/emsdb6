import asyncio
import dns.resolver

FREEMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "mailinator.com", "10minutemail.com",
}

async def check_freemail(email: str) -> bool:
    domain = email.split("@")[-1].lower()
    return await asyncio.to_thread(lambda: domain in free_providers)
