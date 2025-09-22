from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database import async_session
from app.services.email_validator import validate_email
import asyncio

router = APIRouter()


@router.websocket("/ws/validate/multiple")
async def websocket_multiple_email(websocket: WebSocket):
    """
    Validate multiple emails over WebSocket in real-time.
    Expects JSON: { "emails": "email1\nemail2", "user_id": 1 }
    """
    await websocket.accept()

    try:
        # Receive data from frontend
        data = await websocket.receive_json()
        emails_raw = data.get("emails", "")
        user_id = data.get("user_id", 1)

        email_list = [e.strip() for e in emails_raw.splitlines() if e.strip()]
        total = len(email_list)

        # Use async_session factory from database.py
        async with async_session() as db:
            for i, email in enumerate(email_list, start=1):
                result = await validate_email(email=email, db=db, user_id=user_id, deep=True)

                # Send progress update
                await websocket.send_json({
                    "progress": int((i / total) * 100),
                    "result": result
                })

                await asyncio.sleep(0.05)

        # Completion signal
        await websocket.send_json({"done": True})
        await websocket.close()

    except WebSocketDisconnect:
        print("Client disconnected from /ws/validate/multiple")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
