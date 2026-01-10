import os
import random
import logging
from app.services.chatbot_service import chatbot_service
import asyncio

logger = logging.getLogger(__name__)

SUGGESTIONS = {
    "destination": [
        "Bạn có thể đến Đà Lạt, Sapa hoặc Phú Quốc — đều có resort rất đẹp.",
        "Nếu bạn yêu thích biển, Nha Trang và Phú Quốc là lựa chọn tuyệt vời.",
        "Hà Nội có nhiều khách sạn trung tâm tiện cho công tác và tham quan."
    ],
    "room": [
        "Hiện chúng tôi có phòng đơn, phòng đôi và phòng suite cao cấp.",
        "Phòng đôi đang giảm giá 15% trong tuần này.",
        "Phòng suite hướng biển hiện còn trống, bạn có muốn xem chi tiết không?"
    ],
    "branch": [
        "Hệ thống có chi nhánh tại Hà Nội, Đà Nẵng, TP.HCM và Phú Quốc.",
        "Chi nhánh Đà Lạt nằm gần chợ đêm trung tâm.",
        "Chi nhánh TP.HCM có dịch vụ đưa đón sân bay miễn phí."
    ],
    "support": [
        "Bộ phận chăm sóc khách hàng hoạt động 24/7 qua hotline 1800 9999.",
        "Bạn có thể gửi phản hồi qua website hoặc ứng dụng.",
        "Xin vui lòng cho biết vấn đề bạn gặp phải, chúng tôi sẽ hỗ trợ ngay."
    ]
}

def generate_reply(message: str) -> str:
    msg = message.lower()
    
    # Các rule đơn giản
    if any(w in msg for w in ["hotline", "số điện thoại", "liên hệ"]):
        return "Hotline: 1800-9999 (24/7)"
    
    if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
        return "Cảm ơn bạn! Chúc bạn một ngày tốt lành!"
    
    # Gọi service mới (async)
    return asyncio.run(chatbot_service.generate_reply(message))

def _safe_groq_reply(user_message: str) -> str:
    print("\n" + "="*60)
    print("🚀 GROQ API via OpenAI Library")
    
    api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ ERROR: No API key found")
        print("="*60)
        return fallback_reply()
    
    base_url = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    print(f"✅ API Key: Found ({len(api_key)} chars)")
    print(f"📡 Base URL: {base_url}")
    print(f"🤖 Model: {model}")
    print(f"📝 Message: {user_message[:50]}...")
    
    try:
        from openai import OpenAI
        
        print("🔧 Creating OpenAI client for Groq...")
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        print("📤 Sending request to Groq API...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "Bạn là trợ lý ảo của hệ thống khách sạn MelMaybe. Trả lời ngắn gọn bằng tiếng Việt."
                },
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150,
            timeout=20.0
        )
        
        reply = response.choices[0].message.content
        print(f"✅ SUCCESS! Reply: {reply[:80]}...")
        print("="*60)
        return reply
        
    except Exception as e:
        print(f"💥 ERROR: {type(e).__name__}: {str(e)}")
        print("="*60)
        logger.error(f"Groq API failed: {e}", exc_info=True)
        
        # Try alternative method with groq library
        try:
            print("🔄 Trying alternative method with groq library...")
            from groq import Groq
            client = Groq(api_key=api_key)
            
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Bạn là trợ lý khách sạn."},
                    {"role": "user", "content": user_message}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=100
            )
            
            reply = response.choices[0].message.content
            print(f"✅ SUCCESS with groq library! Reply: {reply[:80]}...")
            return reply
        except Exception as groq_error:
            print(f"❌ Groq library also failed: {groq_error}")
            
            # Smart fallback based on message content
            msg_lower = user_message.lower()
            if "lịch sử" in msg_lower:
                return "Khách sạn MelMaybe được thành lập năm 2010, hiện có 5 chi nhánh trên toàn quốc."
            if "giá" in msg_lower or "bao nhiêu" in msg_lower:
                return "Giá phòng từ 1.5 - 5 triệu/đêm tùy loại. Bạn muốn đặt phòng ở đâu?"
            if "hà nội" in msg_lower:
                return "Hà Nội có chi nhánh tại Hoàn Kiếm và Ba Đình với đầy đủ tiện nghi."
            
            return fallback_reply()

def generate_groq_reply(user_message: str) -> str:
    return _safe_groq_reply(user_message)

def fallback_reply() -> str:
    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn MelMaybe. "
        "Tôi có thể hỗ trợ bạn về: đặt phòng, thông tin chi nhánh, dịch vụ khách sạn. "
        "Bạn muốn hỏi gì ạ?"
    )
