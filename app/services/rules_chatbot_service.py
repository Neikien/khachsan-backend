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

    # THÊM NHIỀU TỪ KHÓA HƠN
    if any(w in msg for w in ["đi đâu", "địa điểm", "du lịch", "tham quan", "nên đi"]):
        return random.choice(SUGGESTIONS["destination"])

    if any(w in msg for w in ["phòng", "giá", "đặt", "còn trống", "bao nhiêu", "đơn", "đôi", "suite"]):
        return random.choice(SUGGESTIONS["room"])

    if any(w in msg for w in ["chi nhánh", "địa chỉ", "cơ sở", "ở đâu", "vị trí"]):
        return random.choice(SUGGESTIONS["branch"])

    if any(w in msg for w in ["hỗ trợ", "liên hệ", "phản hồi", "chăm sóc", "hotline"]):
        return random.choice(SUGGESTIONS["support"])

    # TẠM COMMENT GROQ - CHỈ DÙNG RULE-BASED
    return fallback_reply()

def fallback_reply() -> str:
    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn MelMaybe. "
        "Tôi có thể hỗ trợ bạn về: đặt phòng, thông tin chi nhánh, dịch vụ khách sạn. "
        "Bạn muốn hỏi gì ạ?"
    )

# TẠM ẨN GROQ CHO ĐẾN KHI FIX
'''
def generate_groq_reply(user_message: str) -> str:
    api_key = os.getenv("apikey")
    
    if not api_key:
        return "⚠️ Không tìm thấy API key"
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Bạn là trợ lý khách sạn..."},
                {"role": "user", "content": user_message}
            ],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=100
        )
        return response.choices[0].message.content
        
    except ImportError:
        return "❌ Chưa cài package 'groq'. Chạy: pip install groq"
    except Exception as e:
        return f"❌ Lỗi API: {str(e)[:50]}"
'''
