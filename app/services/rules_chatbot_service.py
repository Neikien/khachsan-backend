import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

def generate_reply(message: str) -> str:
    """CHỈ DÙNG AI - không có thứ tự ưu tiên"""
    return _safe_groq_reply(message)

def _safe_groq_reply(user_message: str) -> str:
    print("\n" + "="*60)
    print("🤖 AI-ONLY MODE: Processing question...")
    
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("apikey")
    
    if not api_key:
        print("❌ No API key, using emergency fallback")
        return emergency_fallback(user_message)
    
    system_prompt = """BẠN LÀ TRỢ LÝ ẢO MELMAYBE - HỆ THỐNG 6 KHÁCH SẠN 5 SAO:

=== THÔNG TIN CHÍNH ===
KHÁCH SẠN:
1. InterContinental HÀ NỘI: 1 Lê Thánh Tông, Hoàn Kiếm
2. InterContinental ĐÀ NẴNG: Bãi biển Mỹ Khê
3. InterContinental NHA TRANG: 2 Trần Phú
4. InterContinental ĐÀ LẠT: Đồi Cù
5. InterContinental TP.HCM: Bitexco Tower Q1
6. InterContinental THANH HÓA: Bãi biển Sầm Sơn

GIÁ PHÒNG (VND/đêm):
• HÀ NỘI: Đơn 1.8tr, Đôi 3tr, VIP 6tr
• ĐÀ NẴNG: Đơn 1.5tr, Đôi 2.5tr, VIP 5tr
• NHA TRANG: Đơn 1.6tr, Đôi 2.8tr, VIP 5.5tr
• ĐÀ LẠT: Đơn 1.3tr, Đôi 2.2tr, VIP 4.5tr
• TP.HCM: Đơn 2tr, Đôi 3.5tr, VIP 7tr
• THANH HÓA: Đơn 1.8tr, Đôi 3.6tr, VIP 7tr

HOTLINE: 1800-9999

=== QUY TẮC ===
1. LUÔN dùng thông tin trên
2. Trả lời ngắn gọn, thân thiện, bằng tiếng Việt
3. Nhắc hotline khi cần đặt phòng
4. Nếu không biết: "Hiện tôi chưa có thông tin về..."
5. Với câu chào: Chào hỏi và giới thiệu ngắn về dịch vụ"""
    
    try:
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
            max_tokens=200,
            timeout=15.0
        )
        
        reply = response.choices[0].message.content
        print(f"✅ AI Reply: {reply[:100]}...")
        print("="*60)
        return reply
        
    except Exception as e:
        print(f"💥 AI Error: {e}")
        return emergency_fallback(user_message)

def emergency_fallback(message: str) -> str:
    """Fallback cực kỳ đơn giản khi AI không hoạt động"""
    msg = message.lower()
    
    # CHỈ một vài fallback cực kỳ cơ bản
    if "hotline" in msg or "số điện thoại" in msg:
        return "📞 Hotline: 1800-9999"
    
    if "cảm ơn" in msg:
        return "Cảm ơn bạn! 😊"
    
    return """🏨 Xin chào! Tôi là trợ lý ảo InterContinental.

Hiện hệ thống AI đang bận, vui lòng:
• Gọi hotline 1800-9999 để được hỗ trợ ngay
• Hoặc thử lại sau ít phút

Xin lỗi vì sự bất tiện này!"""
