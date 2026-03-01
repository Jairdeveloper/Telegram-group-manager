"""API routes for chatbot service."""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException


def create_chat_router(actor, storage, app_name: str, app_version: str) -> APIRouter:
    """Create chat routes using injected actor and storage dependencies."""
    router = APIRouter()

    @router.post("/chat")
    async def chat(message: str, session_id: Optional[str] = None):
        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="message required")

        response = actor.process(message)
        storage.save(session_id, message, response.text)

        return {
            "session_id": session_id,
            "message": message,
            "response": response.text,
            "confidence": response.confidence,
            "source": response.source,
            "pattern_matched": response.pattern_matched,
        }

    @router.get("/history/{session_id}")
    async def history(session_id: str):
        return {"session_id": session_id, "history": storage.get_history(session_id)}

    @router.get("/stats")
    async def stats():
        return {
            "app_name": app_name,
            "version": app_version,
            "total_sessions": len(storage.data),
            "total_messages": sum(len(msgs) for msgs in storage.data.values()),
        }

    return router
