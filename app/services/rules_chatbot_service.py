# app/services/rules_chatbot_service.py
import os
import groq
from app.core.config import config  # ← IMPORT CONFIG

def generate_reply(user_message: str) -> str:
    """
    Generate reply using Groq API
    """
    # Lấy API key từ biến môi trường
    api_key = config.apikey or os.getenv("GROQ_API_KEY") or os.getenv("apikey")
    
    if not api_key:
        return "Chatbot đang bảo trì. Vui lòng thử lại sau."
    
    try:
        # Khởi tạo Groq client
        client = groq.Client(api_key=api_key)
        
        # System prompt cho chatbot khách sạn
        system_prompt = """Bạn là trợ lý ảo của hệ thống khách sạn MelMaybe. 
        Hãy trả lời các câu hỏi về:
        1. Đặt phòng, hủy phòng
        2. Thông tin khách sạn, giá cả
        3. Dịch vụ (spa, nhà hàng, hồ bơi)
        4. Chính sách, quy định
        
        Giữ câu trả lời ngắn gọn, thân thiện, bằng tiếng Việt."""
        
        # Gọi Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama3-70b-8192",  # Hoặc model khác: "mixtral-8x7b-32768", "gemma-7b-it"
            temperature=0.7,
            max_tokens=500
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Lỗi Groq API: {str(e)}")
        return "Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau."
