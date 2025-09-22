from fastapi import (
    APIRouter, Depends, UploadFile, File, Form, Request, HTTPException
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.email_validator import validate_email
from app.csrf import validate_csrf_token
import asyncio
import json

router = APIRouter()

@router.post("/email/validate/batch/stream")
async def validate_batch_stream(
    request: Request,
    csrf_token: str = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    # 🔒 Validate CSRF
    if not validate_csrf_token(request, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    # Collect emails from all files
    emails = []
    for file in files:
        contents = await file.read()
        file_emails = [line.strip() for line in contents.decode().splitlines() if line.strip()]
        emails.extend(file_emails)

    total = len(emails)
    if total == 0:
        return {"error": "No valid emails found in uploaded files."}

    async def event_stream():
        for i, email in enumerate(emails, start=1):
            result = await validate_email(email, db, user_id=1, deep=True)
            data = {"progress": int((i / total) * 100), "result": result}
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.2)

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
