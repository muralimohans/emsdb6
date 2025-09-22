import asyncio
from collections import defaultdict

# Stores queues for per-session updates
_sessions = defaultdict(asyncio.Queue)

# Stores dashboard stats
_dashboard = asyncio.Queue()

def create_session(emails):
    import uuid
    session_id = str(uuid.uuid4())
    _sessions[session_id] = asyncio.Queue()
    return session_id

async def push_progress(session_id, data):
    """Push per-email progress to a session queue"""
    if session_id in _sessions:
        await _sessions[session_id].put(data)
        # Also push summary to dashboard
        await _dashboard.put(data)

async def stream_session(session_id):
    """Generator for SSE per session"""
    queue = _sessions[session_id]
    while True:
        data = await queue.get()
        yield f"data: {data}\n\n"
        if data.get("done"):
            break

async def stream_dashboard():
    """Generator for SSE dashboard updates"""
    while True:
        import asyncio
        await asyncio.sleep(1)  # 1 second interval
        summary = {"active_sessions": []}
        for sid, q in _sessions.items():
            summary["active_sessions"].append({"session_id": sid})
        yield f"data: {summary}\n\n"
