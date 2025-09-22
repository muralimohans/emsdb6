import smtplib
import socket

def check_greylist(email: str, mx_host: str) -> bool:
    """
    Attempt simple SMTP verification with retry.
    If first RCPT is temporarily rejected (greylisted), retry once.
    """
    try:
        server = smtplib.SMTP(timeout=5)
        server.connect(mx_host)
        server.helo(socket.gethostname())
        server.mail("test@example.com")
        code, _ = server.rcpt(email)
        if code == 450:  # Greylist temporary failure
            code, _ = server.rcpt(email)  # retry once
        server.quit()
        return code == 250
    except Exception:
        return False
