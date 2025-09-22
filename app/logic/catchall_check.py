import smtplib
import socket
import dns.resolver

def check_catchall(email: str) -> bool:
    """
    Detect if domain is catch-all
    Simple attempt: test a random email on the domain
    """
    try:
        domain = email.split("@")[1]
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_host = str(mx_records[0].exchange)

        server = smtplib.SMTP(timeout=5)
        server.connect(mx_host)
        server.helo(socket.gethostname())
        # Send to a random address
        code, _ = server.rcpt(f"randomcatchall_{domain}@{domain}")
        server.quit()
        return code == 250
    except Exception:
        return False
