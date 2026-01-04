# app/services/rules_chatbot_service.py - SỬA PHẦN GROQ
import os
import random

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

    if any(w in msg for w in ["đi đâu", "địa điểm", "du lịch", "tham quan"]):
        return random.choice(SUGGESTIONS["destination"])

    if any(w in msg for w in ["phòng", "giá", "đặt", "còn trống"]):
        return random.choice(SUGGESTIONS["room"])

    if any(w in msg for w in ["chi nhánh", "địa chỉ", "cơ sở"]):
        return random.choice(SUGGESTIONS["branch"])

    if any(w in msg for w in ["hỗ trợ", "liên hệ", "phản hồi", "chăm sóc"]):
        return random.choice(SUGGESTIONS["support"])

    # Nếu không match rule, THỬ dùng Groq AI
    try:
        return generate_groq_reply(message)
    except:
        # Fallback nếu Groq lỗi
        return fallback_reply()

def generate_groq_reply(user_message: str) -> str:
    """Generate reply using Groq API (chỉ chạy nếu có API key)"""
    api_key = os.getenv("apikey")  # Đọc trực tiếp từ biến môi trường
    
    if not api_key or api_key == "":
        return fallback_reply()  # Không có API key, dùng fallback
    
    try:
        from groq import Groq  # Import trong function để tránh lỗi nếu không cài
        
        client = Groq(api_key=api_key)  # ← ĐÚNG: Groq() chứ không phải groq.Client()
        
        system_prompt = """Bạn là trợ lý ảo của hệ thống khách sạn MelMaybe."""
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except ImportError:
        return "Chatbot AI đang bảo trì. Vui lòng thử lại sau."
    except Exception as e:
        print(f"❌ Lỗi Groq API: {type(e).__name__}: {e}")
        return fallback_reply()

def fallback_reply() -> str:
    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn MelMaybe. "
        "Tôi có thể hỗ trợ bạn về: đặt phòng, thông tin chi nhánh, dịch vụ khách sạn. "
        "Bạn muốn hỏi gì ạ?"
    )
