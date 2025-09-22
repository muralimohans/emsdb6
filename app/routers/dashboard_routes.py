from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models.user import User
from app.utils.sse import _sessions  # active SSE sessions

import asyncio
import json

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# GET: Dashboard Page
# -------------------------
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Render the user dashboard with credit balance.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "credits": user.credits,
        },
    )


# -------------------------
# GET: SSE Progress Stream
# -------------------------
@router.get("/dashboard/progress")
async def dashboard_progress():
    """
    SSE endpoint that streams active session progress to the dashboard.
    """

    async def event_generator():
        while True:
            await asyncio.sleep(1)  # poll every 1 second

            summary = {
                "total_sessions": len(_sessions),
                "active_sessions": [{"session_id": sid} for sid in _sessions.keys()],
            }

            # Always JSON-encode for SSE
            yield f"data: {json.dumps(summary)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
