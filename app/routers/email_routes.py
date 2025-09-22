import csv
import io
from fastapi import (
    APIRouter, Request, Form, UploadFile, File, Depends,
    WebSocket, WebSocketDisconnect
)
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.csrf import generate_csrf_token, validate_csrf_token
from app.models.user import User
from app.dependencies import get_current_user
from app.services.email_validator import validate_email
from app.utils.sse import push_progress
from app.core.websocket_manager import manager
import json
import asyncio
from app.tasks.email_tasks import validate_single_email, validate_multiple_emails, validate_bulk_emails, validate_batch_emails

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# -------------------------
# Single Validation
# -------------------------
@router.get("/email/validate/multiple", response_class=HTMLResponse)
async def get_multiple_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Render the form for multiple email validation with CSRF token.
    """
    csrf_token = generate_csrf_token(request)  # pass request to store token in session

    return templates.TemplateResponse(
        "validate_multiple_form.html",
        {
            "request": request,
            "csrf_token": csrf_token,
            "user": current_user
        },
    )


@router.get("/email/validate/bulk", response_class=HTMLResponse)
async def get_bulk_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Render the bulk email validation form with a CSRF token.
    """
    csrf_token = generate_csrf_token(request)  # ✅ pass request to store token in session

    return templates.TemplateResponse(
        "validate_bulk_form.html",
        {
            "request": request,
            "csrf_token": csrf_token,
            "user": current_user
        },
    )

@router.get("/email/validate/batch", response_class=HTMLResponse)
async def show_batch_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Render the batch email validation form with CSRF protection.
    """
    csrf_token = generate_csrf_token(request)  # ✅ store token in session

    return templates.TemplateResponse(
        "validate_batch.html",
        {
            "request": request,
            "csrf_token": csrf_token,
            "user": current_user,
            "results": None
        },
    )
# -------------------------
# WebSocket for live updates
# -------------------------
@router.websocket("/ws/validation/progress")
async def validation_progress(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ✅ Single validation (async via Celery)
@router.post("/email/validate")
async def validate_single(
    request: Request,
    email: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    task = validate_single_email.delay(email, current_user.id)
    return {"message": "Validation started", "task_id": task.id}


# ✅ Bulk validation (async via Celery)
@router.post("/email/validate/bulk")
async def validate_bulk(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
):
    emails = [line.decode("utf-8").strip() for line in file.file.readlines() if line.strip()]
    task = bulk_validate_emails.delay(emails, current_user.id)
    return {"message": "Bulk validation started", "task_id": task.id}


# ✅ Task status check
@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "SUCCESS":
        return {"status": "success", "result": task.result}
    elif task.state == "FAILURE":
        return {"status": "failure", "error": str(task.info)}
    return {"status": task.state}