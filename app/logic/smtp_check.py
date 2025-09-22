import smtplib
import socket
import dns.resolver

def check_smtp(email: str) -> bool:
    """Attempt SMTP handshake to verify mailbox exists"""
    try:
        domain = email.split("@")[1]
        mx_records = dns.resolver.resolve(domain, "MX")
        mx_host = str(mx_records[0].exchange)
        server = smtplib.SMTP(timeout=5)
        server.connect(mx_host)
        server.helo(socket.gethostname())
        server.mail("test@example.com")
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except Exception:
        return False
