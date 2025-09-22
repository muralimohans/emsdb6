import uuid
import asyncio
import json
import csv
from io import StringIO
from typing import List

from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.email_validator import validate_email

router = APIRouter()

# In-memory task store { session_id: [emails] }
bulk_sessions = {}

@router.post("/email/validate/bulk/start")
async def start_bulk_validation(file: UploadFile = File(...)):
    """
    Accepts bulk email file (.txt or .csv) and returns a session_id for WebSocket progress tracking.
    """
    content = await file.read()
    text = content.decode("utf-8")

    # Extract emails (handle CSV or plain text)
    emails: List[str] = []
    if file.filename.endswith(".csv"):
        reader = csv.reader(StringIO(text))
        for row in reader:
            if row:  # pick first column
                emails.append(row[0].strip())
    else:
        emails = [line.strip() for line in text.splitlines() if line.strip()]

    if not emails:
        return {"error": "No emails found in file."}

    session_id = str(uuid.uuid4())
    bulk_sessions[session_id] = emails
    return {"session_id": session_id, "count": len(emails)}


@router.websocket("/ws/validation/progress/{session_id}")
async def bulk_validation_progress(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    await websocket.accept()

    if session_id not in bulk_sessions:
        await websocket.send_text(json.dumps({"error": "Invalid session_id"}))
        await websocket.close()
        return

    emails = bulk_sessions.pop(session_id)  # remove after use
    total = len(emails)

    try:
        for i, email in enumerate(emails, start=1):
            # Run full validation (fresh, no cache)
            result = await validate_email(email, db, user_id=1, deep=True)

            percent = int((i / total) * 100)
            await websocket.send_text(json.dumps({
                "percent": percent,
                "result": result
            }))

            await asyncio.sleep(0.1)  # small delay to avoid flooding

        # Done
        await websocket.send_text(json.dumps({"done": True}))

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {session_id}")
    finally:
        await websocket.close()
