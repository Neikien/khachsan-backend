# app/services/rules_chatbot_service.py
import os
import logging
from app.services.chatbot_service import chatbot_service

logger = logging.getLogger(__name__)

def generate_reply(message: str) -> str:
    """Main reply function - calls chatbot service"""
    msg = message.lower()
    
    # Quick responses for common questions
    if any(w in msg for w in ["hotline", "số điện thoại", "liên hệ"]):
        return "📞 Hotline hỗ trợ 24/7: 1800-9999"
    
    if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
        return "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
    
    if any(w in msg for w in ["xin chào", "hello", "hi", "chào"]):
        return "Xin chào! Tôi là trợ lý ảo MelMaybe. Tôi có thể giúp gì cho bạn?"
    
    # Call the main chatbot service (which will handle database queries)
    return chatbot_service.sync_generate_reply(message)

def generate_groq_reply(user_message: str) -> str:
    """Legacy function for backward compatibility"""
    return _safe_groq_reply(user_message)

def _safe_groq_reply(user_message: str) -> str:
    """Legacy Groq function - kept for compatibility"""
    print("\n" + "="*60)
    print("⚠️ Using legacy Groq function (new service recommended)")
    
    api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return fallback_reply()
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": "Bạn là trợ lý khách sạn."
                },
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception:
        return fallback_reply()

def fallback_reply() -> str:
    """Simple fallback"""
    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn MelMaybe. "
        "Hiện tôi có thể giúp bạn tìm thông tin khách sạn, phòng trống, và đặt phòng. "
        "Bạn muốn hỏi gì ạ?"
    )
