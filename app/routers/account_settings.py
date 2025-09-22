# app/routes/account_settings.py
import shutil
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.csrf import generate_csrf_token
from passlib.context import CryptContext
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIR = "app/static/uploads/profile_pics"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --------------------
# GET: Account Settings
# --------------------
@router.get("/account/settings")
async def get_account_settings(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        "account_settings.html",
        {
            "request": request,
            "user": current_user,
            "csrf_token": csrf_token
        }
    )


# --------------------
# POST: Update Account Info
# --------------------
@router.post("/account/settings")
async def update_account_settings(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(None),
    confirm_password: str = Form(None),
    profile_pic: UploadFile = File(None),
    notify_email: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    message = None

    # Update username/email
    current_user.username = username
    current_user.email = email
    current_user.notify_email = notify_email

    # Update password if provided
    if password:
        if password != confirm_password:
            message = "Passwords do not match!"
        else:
            current_user.hashed_password = pwd_context.hash(password)
            message = "Account updated successfully with new password"
    else:
        if not message:
            message = "Account updated successfully"

    # Save profile picture
    if profile_pic:
        file_ext = os.path.splitext(profile_pic.filename)[1]
        filename = f"user_{current_user.id}{file_ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(profile_pic.file, buffer)
        current_user.profile_pic = f"/static/uploads/profile_pics/{filename}"

    # Commit changes
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        "account_settings.html",
        {
            "request": request,
            "user": current_user,
            "csrf_token": csrf_token,
            "message": message
        }
    )
