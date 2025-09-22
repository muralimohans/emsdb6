import dns.resolver
import aiodns

async def check_dns_record(email: str) -> bool:
    domain = email.split("@")[-1]
    try:
        return await asyncio.to_thread(
            lambda: bool(dns.resolver.resolve(domain, "A"))
        )
    except Exception:
        return False
