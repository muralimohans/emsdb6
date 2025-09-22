from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import HTTPException, Request
from app.config import settings
import secrets

csrf_serializer = URLSafeSerializer(settings.secret_key, salt="csrf-token")


def generate_csrf_token(request: Request) -> str:
    """
    Generate a CSRF token, store it in session, and return the signed token.
    """
    raw_token = csrf_serializer.dumps(secrets.token_hex(32))  # signed token
    request.session["csrf_token"] = raw_token
    return raw_token


def validate_csrf_token(request: Request, token: str) -> bool:
    """
    Validate CSRF token by checking session and signature.
    """
    session_token = request.session.get("csrf_token")
    if not session_token:
        raise HTTPException(status_code=403, detail="CSRF token missing in session")

    try:
        # Verify signature
        csrf_serializer.loads(token)
    except BadSignature:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    # Optional: Compare with session token
    if token != session_token:
        raise HTTPException(status_code=403, detail="CSRF token mismatch")

    return True
