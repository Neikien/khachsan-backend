# app/services/rules_chatbot_service.py
from app.services.chatbot_service import chatbot_service

def generate_reply(message: str) -> str:
    """Main reply function - calls chatbot service"""
    return chatbot_service.sync_generate_reply(message)

def generate_groq_reply(user_message: str) -> str:
    """Legacy function for backward compatibility"""
    return chatbot_service.sync_generate_reply(user_message)

def fallback_reply() -> str:
    """Simple fallback"""
    return chatbot_service.sync_generate_reply("")
