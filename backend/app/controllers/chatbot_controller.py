from fastapi import APIRouter
from app.schemas.chatbot_schema import ChatRequest, ChatResponse
from app.services.chatbot_service import generate_reply

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/ask", response_model=ChatResponse)
async def ask_bot(request: ChatRequest):
    reply = generate_reply(request.message)
    return ChatResponse(reply=reply)
