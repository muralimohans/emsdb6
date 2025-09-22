from fastapi import APIRouter, Request, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from app.database import get_db
from app.services.email_validator import validate_email
from app.dependencies import get_current_user
from app.models.user import User
from app.csrf import generate_csrf_token, validate_csrf_token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/email/validate/single")
def single_email_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Render the email input form with CSRF token.
    """
    csrf_token = generate_csrf_token(request)  # Generate token per session/request

    return templates.TemplateResponse(
        "single_email_form.html",
        {
            "request": request,
            "csrf_token": csrf_token,
            "user": current_user
        }
    )


@router.post("/email/validate/single")
async def validate_single_email_route(
    request: Request,
    email: str = Form(...),
    csrf_token: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate a single email synchronously and render results in HTML.
    Deducts 1 credit inside validate_email.
    """
    # ✅ CSRF validation
    if not validate_csrf_token(request, csrf_token):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    # ✅ Check user credits
    if current_user.credits < 1:
        raise HTTPException(status_code=400, detail="Not enough credits")

    # ✅ Run email validation
    result = await validate_email(
        email=email,
        db=db,
        user_id=current_user.id,
        deep=True
    )

    # ✅ Generate a new CSRF token for the next form submission
    new_csrf_token = generate_csrf_token(request)

    return templates.TemplateResponse(
        "validate_single.html",
        {
            "request": request,
            "result": result,
            "csrf_token": new_csrf_token,  # pass request to generate token
            "user": current_user
        }
    )

