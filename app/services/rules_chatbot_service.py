import os
import logging

logger = logging.getLogger(__name__)

def generate_reply(message: str) -> str:
    msg = message.lower()

    # Giữ các rule đơn giản
    if any(w in msg for w in ["hotline", "số điện thoại", "liên hệ"]):
        return "📞 Hotline hỗ trợ 24/7: 1800-9999"
    
    if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
        return "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
    
    if any(w in msg for w in ["xin chào", "hello", "hi", "chào"]):
        return "Xin chào! Tôi là trợ lý ảo MelMaybe. Tôi có thể giúp gì cho bạn?"
    
    # Thông tin thực tế từ database
    if any(w in msg for w in ["khách sạn", "hotel", "chi nhánh", "ở đâu"]):
        return "🏨 **Hệ thống MelMaybe có 5 khách sạn 5 sao:**\n• Hà Nội: 1 Lê Thánh Tông, Hoàn Kiếm\n• Đà Nẵng: Bãi biển Mỹ Khê\n• Nha Trang: 2 Trần Phú\n• Đà Lạt: Đồi Cù, phường 1\n• TP.HCM: Bitexco Financial Tower, Quận 1"
    
    if any(w in msg for w in ["phòng đơn", "đơn", "single room"]):
        return "🛏️ **Phòng Đơn:** 1.5 - 2 triệu VND/đêm"
    
    if any(w in msg for w in ["phòng đôi", "đôi", "double room"]):
        return "🛏️ **Phòng Đôi:** 2.5 - 3 triệu VND/đêm"
    
    if any(w in msg for w in ["phòng vip", "vip", "suite"]):
        return "🛏️ **Phòng VIP:** 5 triệu VND/đêm"
    
    if any(w in msg for w in ["phòng", "giá", "price", "bao nhiêu"]):
        return "💰 **Bảng giá phòng:**\n• Phòng Đơn: 1.5 - 2 triệu\n• Phòng Đôi: 2.5 - 3 triệu\n• Phòng VIP: 5 triệu\n📞 Đặt phòng: 1800-9999"
    
    if any(w in msg for w in ["đặt phòng", "đặt", "book", "booking"]):
        return "📋 **Để đặt phòng, vui lòng:**\n1. Chọn khách sạn trong 5 địa điểm trên\n2. Chọn loại phòng và ngày\n3. Gọi hotline 1800-9999\n4. Hoặc đến trực tiếp khách sạn"
    
    if any(w in msg for w in ["dịch vụ", "service", "tiện ích"]):
        return "⭐ **Dịch vụ khách sạn:**\n• WiFi miễn phí\n• Bể bơi\n• Nhà hàng\n• Spa & massage\n• Trung tâm hội nghị\n• Đưa đón sân bay (một số chi nhánh)"
    
    # Nếu không match rule nào, dùng Groq AI
    return _safe_groq_reply(message)

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
                    "content": "Bạn là trợ lý ảo của hệ thống khách sạn MelMaybe (5 khách sạn 5 sao tại Hà Nội, Đà Nẵng, Nha Trang, Đà Lạt, TP.HCM). Giá phòng: Đơn 1.5-2tr, Đôi 2.5-3tr, VIP 5tr. Hotline: 1800-9999. Trả lời ngắn gọn bằng tiếng Việt."
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
        
        # Fallback thông minh
        msg_lower = user_message.lower()
        
        if any(w in msg_lower for w in ["thời tiết", "weather"]):
            return "Tôi là trợ lý khách sạn, không có thông tin thời tiết. Bạn có thể hỏi về khách sạn, phòng, giá cả hoặc dịch vụ."
        
        if any(w in msg_lower for w in ["ăn", "uống", "nhà hàng", "food"]):
            return "Mỗi khách sạn MelMaybe đều có nhà hàng phục vụ ẩm thực Việt Nam và quốc tế. Giờ mở cửa: 6:00 - 22:00."
        
        if any(w in msg_lower for w in ["wifi", "internet"]):
            return "Tất cả khách sạn MelMaybe đều có WiFi miễn phí tốc độ cao trong toàn bộ khuôn viên."
        
        return fallback_reply()

def generate_groq_reply(user_message: str) -> str:
    return _safe_groq_reply(user_message)

def fallback_reply() -> str:
    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn MelMaybe. "
        "Tôi có thể giúp bạn:\n"
        "• Tìm thông tin 5 khách sạn 5 sao\n"
        "• Tư vấn giá phòng (Đơn 1.5-2tr, Đôi 2.5-3tr, VIP 5tr)\n"
        "• Hỗ trợ đặt phòng\n"
        "• Cung cấp hotline: 1800-9999\n"
        "Bạn muốn hỏi gì ạ?"
    )
