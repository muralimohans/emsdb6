from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

from app.models.user import User
from app.database import get_db
from app.crud.user_crud import user_crud
from app.csrf import generate_csrf_token, validate_csrf_token
from app.utils.security import get_password_hash

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------------------------------------------
# Register
# -------------------------------------------------------------------
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        "register.html", {"request": request, "csrf_token": csrf_token}
    )


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # ✅ CSRF check
    validate_csrf_token(request, csrf_token)

    # ✅ Prevent duplicate registration
    existing_user = await user_crud.get_by_email(db, email)
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Email already registered",
                "csrf_token": generate_csrf_token(request),
            },
            status_code=400,
        )

    # ✅ Hash password
    hashed_password = get_password_hash(password)

    # ✅ Save user
    await user_crud.create_user(db, email, hashed_password)

    # ✅ Redirect to login
    return RedirectResponse(url="/login", status_code=303)


# -------------------------------------------------------------------
# Login
# -------------------------------------------------------------------
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        "login.html", {"request": request, "csrf_token": csrf_token}
    )


@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # ✅ CSRF check
    validate_csrf_token(request, csrf_token)

    # ✅ Fetch user
    user = await user_crud.get_by_email(db, email)

    if not user or not pwd_context.verify(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password",
                "csrf_token": generate_csrf_token(request),
            },
            status_code=400,
        )

    # ✅ Successful login → store user_id in session
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)
