# routes/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.services.langgraph_service import stream_chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    return StreamingResponse(
        stream_chat(req.message, req.thread_id),
        media_type="text/plain"
    )
