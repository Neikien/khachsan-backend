import os
import logging

logger = logging.getLogger(__name__)

def generate_reply(message: str) -> str:
    msg = message.lower()

    # Quick responses
    if any(w in msg for w in ["hotline", "số điện thoại", "liên hệ"]):
        return "📞 Hotline đặt phòng 24/7: 1800-9999"
    
    if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
        return "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
    
    if any(w in msg for w in ["xin chào", "hello", "hi", "chào"]):
        return "Xin chào! Tôi là trợ lý ảo MelMaybe. Tôi có thể giúp gì cho bạn?"
    
    # Basic info from database (fallback khi AI không hoạt động)
    if any(w in msg for w in ["khách sạn", "hotel", "chi nhánh", "ở đâu"]):
        return "🏨 **Hệ thống InterContinental có 6 khách sạn 5 sao:**\n• Hà Nội : 1 Lê Thánh Tông\n• Đà Nẵng : Bãi biển Mỹ Khê\n• Nha Trang : 2 Trần Phú\n• Đà Lạt : Đồi Cù\n• TP.HCM : Bitexco Tower Q1\n• Thanh Hóa : Bãi biển Sầm Sơn"
    
    if any(w in msg for w in ["phòng đơn", "đơn"]):
        return "🛏️ **Phòng Đơn:** 1.3 - 2 triệu VND/đêm (tùy địa điểm)"
    
    if any(w in msg for w in ["phòng đôi", "đôi"]):
        return "🛏️ **Phòng Đôi:** 2.2 - 3.6 triệu VND/đêm"
    
    if any(w in msg for w in ["phòng vip", "vip"]):
        return "🛏️ **Phòng VIP:** 4.5 - 7 triệu VND/đêm"
    
    if any(w in msg for w in ["giá", "price", "bao nhiêu"]):
        return "💰 **Giá tham khảo:**\n• Đơn: 1.3-2tr\n• Đôi: 2.2-3.6tr\n• VIP: 4.5-7tr\n📞 Chi tiết: 1800-9999"
    
    # Dùng AI cho các câu hỏi phức tạp
    return _safe_groq_reply(message)

def _safe_groq_reply(user_message: str) -> str:
    print("\n" + "="*60)
    print("🚀 GROQ AI WITH FULL DATABASE KNOWLEDGE")
    
    api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ No API key, using fallback")
        return fallback_reply()
    
    # OPTIMIZED SYSTEM PROMPT với toàn bộ database
    system_prompt = """BẠN LÀ TRỢ LÝ ẢO MELMAYBE - HỆ THỐNG 6 KHÁCH SẠN 5 SAO:

=== KHÁCH SẠN (MÃ KHÁCH SẠN - MaKS) ===
1. InterContinental HÀ NỘI (291): 1 Lê Thánh Tông, Hoàn Kiếm - Quản lý: Nguyễn Văn Toàn (0909123456)
2. InterContinental ĐÀ NẴNG (432): Bãi biển Mỹ Khê - Quản lý: Trần Thị Hương (0918234567)
3. InterContinental NHA TRANG (493): 2 Trần Phú - Quản lý: Lê Minh Tuấn (0927345678) - Biết tiếng Anh/Nhật
4. InterContinental ĐÀ LẠT (684): Đồi Cù - Quản lý: Phạm Thị Lan (0936456789) - Chuyên honeymoon
5. InterContinental TP.HCM (795): Bitexco Tower Q1 - Quản lý: Hoàng Văn Đức (0945567890)
6. InterContinental THANH HÓA (366): Bãi biển Sầm Sơn

=== GIÁ PHÒNG (VND/đêm) ===
• HÀ NỘI: Đơn 1.8tr, Đôi 3tr, VIP 6tr
• ĐÀ NẴNG: Đơn 1.5tr, Đôi 2.5tr, VIP 5tr
• NHA TRANG: Đơn 1.6tr, Đôi 2.8tr, VIP 5.5tr
• ĐÀ LẠT: Đơn 1.3tr, Đôi 2.2tr, VIP 4.5tr
• TP.HCM: Đơn 2tr, Đôi 3.5tr, VIP 7tr
• THANH HÓA: Đơn 1.8tr, Đôi 3.6tr, VIP 7tr

=== DỊCH VỤ ===
• Buffet sáng: 250,000đ (6:00-10:00)
• Nhà hàng: 500,000đ (10:00-22:00)
• Quầy bar: 150,000đ (16:00-23:00)
• Tiệc BBQ: 800,000đ
• Gym: 100,000đ (24/7)
• Bể bơi: 50,000đ
• Spa: 600,000đ
• Xông hơi: 150,000đ
• Karaoke: 500,000đ
• Tiệc cưới: 5,000,000đ

=== QUY TẮC TRẢ LỜI ===
1. CHỈ dùng thông tin trên, KHÔNG bịa ra
2. Không biết → "Hiện chưa có thông tin về..."
4. Nhắc hotline 3636-2929 để đặt phòng/dịch vụ
5. Trả lời bằng tiếng Việt, ngắn gọn, thân thiện
6. Với dịch vụ: nêu giá và thời gian phục vụ
7. Với liên hệ: cung cấp số quản lý tương ứng"""

    try:
        from openai import OpenAI
        
        print("🤖 Sending to Groq AI...")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=250,
            timeout=20.0
        )
        
        reply = response.choices[0].message.content
        print(f"✅ AI SUCCESS! Reply: {reply[:100]}...")
        print("="*60)
        return reply
        
    except Exception as e:
        print(f"💥 AI Error: {type(e).__name__}: {str(e)}")
        logger.error(f"Groq API failed: {e}")
        
        # Smart fallback
        msg_lower = user_message.lower()
        
        if any(w in msg_lower for w in ["thời tiết", "weather", "nhiệt độ"]):
            return "Tôi là trợ lý khách sạn. Bạn có thể hỏi về khách sạn, phòng, giá cả, dịch vụ hoặc hotline 1800-9999."
        
        if any(w in msg_lower for w in ["ăn", "uống", "nhà hàng", "food", "đồ ăn"]):
            return "Mỗi InterContinental đều có: Buffet sáng (250k, 6-10h), Nhà hàng (500k, 10-22h), Quầy bar (150k, 16-23h)."
        
        if any(w in msg_lower for w in ["wifi", "internet", "mạng"]):
            return "Tất cả InterContinental đều có WiFi miễn phí tốc độ cao."
        
        if any(w in msg_lower for w in ["spa", "massage", "thư giãn"]):
            return "Dịch vụ spa tại InterContinental: 600,000 VND cho 60 phút massage."
        
        return fallback_reply()

def generate_groq_reply(user_message: str) -> str:
    return _safe_groq_reply(user_message)

def fallback_reply() -> str:
    return """🏨 **Xin chào! Tôi là trợ lý ảo InterContinental.**

Tôi có thể giúp bạn:
• Tìm 6 khách sạn 5 sao (Hà Nội, Đà Nẵng, Nha Trang, Đà Lạt, TP.HCM, Thanh Hóa)
• Tư vấn giá phòng chi tiết theo từng địa điểm
• Giới thiệu dịch vụ: buffet, nhà hàng, spa, gym, bể bơi
• Cung cấp số điện thoại quản lý từng khách sạn
• Hỗ trợ đặt phòng qua hotline 1800-9999

Bạn muốn hỏi về điều gì cụ thể ạ?"""
