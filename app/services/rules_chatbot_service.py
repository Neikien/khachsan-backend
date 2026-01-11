import os
import logging
from typing import Dict, List
from collections import defaultdict
from openai import OpenAI  # Import ở cấp module

logger = logging.getLogger(__name__)

# ========== BỘ NHỚ HỘI THOẠI ==========
_conversation_history: Dict[str, List[Dict]] = defaultdict(list)
_MAX_HISTORY_LENGTH = 6

def _get_user_history(user_id: str = "default") -> List[Dict]:
    """Lấy lịch sử hội thoại của user"""
    return _conversation_history.get(user_id, [])

def _add_to_history(user_id: str = "default", role: str = "user", content: str = ""):
    """Thêm tin nhắn vào lịch sử"""
    history = _conversation_history[user_id]
    history.append({"role": role, "content": content})
    
    if len(history) > _MAX_HISTORY_LENGTH:
        _conversation_history[user_id] = history[-_MAX_HISTORY_LENGTH:]

def _clear_history(user_id: str = "default"):
    """Xóa lịch sử hội thoại"""
    if user_id in _conversation_history:
        del _conversation_history[user_id]

# ========== HÀM CŨ ĐƯỢC GIỮ NGUYÊN ==========
def _safe_groq_reply(user_message: str) -> str:
    """Xử lý câu trả lời từ Groq AI với fallback an toàn"""
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
6. InterContinental THANH HÓA (366): Bãi biển Sầm Sơn - Quản lý: Nguyễn Thị Mai(0912345678')

=== GIÁ PHÒNG (VND/đêm) ===
• HÀ NỘI: Đơn 1.8tr, Đôi 3tr, VIP 6tr
• ĐÀ NẴNG: Đơn 1.5tr, Đôi 2.5tr, VIP 5tr
• NHA TRANG: Đơn 1.6tr, Đôi 2.8tr, VIP 5.5tr
• ĐÀ LẠT: Đơn 1.3tr, Đôi 2.2tr, VIP 4.5tr
• TP.HCM: Đơn 2tr, Đôi 3.5tr, VIP 7tr
• THANH HÓA: Đơn 1.8tr, Đôi 3.6tr, VIP 7tr

=== DỊCH VỤ (GIÁ CHI TIẾT) ===
• Buffet sáng: 250,000 VND/người (6:00-10:00)
• Nhà hàng à la carte: 500,000 - 1,500,000 VND/người (10:00-22:00)
• Quầy bar: 150,000 - 300,000 VND/đồ uống (16:00-23:00)
• Tiệc BBQ hải sản: 800,000 VND/người (18:00-22:00)
• Phòng Gym: MIỄN PHÍ cho khách lưu trú (24/7)
• Bể bơi: MIỄN PHÍ cho khách lưu trú (6:00-22:00)
• Spa & Massage: 600,000 - 1,200,000 VND/60 phút (9:00-21:00)
• Xông hơi: 150,000 VND/người (9:00-21:00)
• Phòng Karaoke: 500,000 - 1,000,000 VND/giờ (14:00-24:00)
• Tiệc cưới/Event: 5,000,000 - 20,000,000 VND/bữa (tùy quy mô)

=== QUY TẮC TRẢ LỜI ===
1. CHỈ dùng thông tin trên, KHÔNG bịa ra
2. Khi hỏi về dịch vụ: PHẢI nêu giá và thời gian phục vụ
3. "Sọa" = "Spa" (do lỗi chính tả)
4. Khi user hỏi "dịch vụ spa" hoặc "sọa": trả lời đầy đủ giá và thời gian
5. Nhắc hotline 1800-9999 để đặt dịch vụ
6. Trả lời bằng tiếng Việt, ngắn gọn, thân thiện"""
    
    try:
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
            max_tokens=300,
            timeout=20.0
        )
        
        reply = response.choices[0].message.content
        print(f"✅ AI SUCCESS! Reply: {reply[:100]}...")
        print("="*60)
        return reply
        
    except Exception as e:
        print(f"💥 AI Error: {type(e).__name__}: {str(e)}")
        logger.error(f"Groq API failed: {e}")
        
        # Smart fallback - CẬP NHẬT: Thêm xử lý "sọa"
        msg_lower = user_message.lower()
        
        # Xử lý lỗi chính tả "sọa" = "spa"
        if "sọa" in msg_lower or "spa" in msg_lower or "massage" in msg_lower or "thư giãn" in msg_lower:
            return "💆 **Dịch vụ Spa tại InterContinental:**\n• Massage thư giãn: 600,000 VND/60 phút\n• Massage trị liệu: 800,000 VND/60 phút\n• Gói Spa cao cấp: 1,200,000 VND/90 phút\n⏰ Thời gian: 9:00 - 21:00 hàng ngày\n📞 Đặt lịch: 1800-9999"
        
        if any(w in msg_lower for w in ["ăn", "uống", "nhà hàng", "food", "đồ ăn", "buffet"]):
            return "🍽️ **Dịch vụ ẩm thực:**\n• Buffet sáng: 250,000 VND (6:00-10:00)\n• Nhà hàng: 500,000-1,500,000 VND (10:00-22:00)\n• Quầy bar: 150,000-300,000 VND (16:00-23:00)\n• BBQ: 800,000 VND (18:00-22:00)"
        
        if any(w in msg_lower for w in ["thời tiết", "weather", "nhiệt độ"]):
            return "Tôi là trợ lý khách sạn. Bạn có thể hỏi về khách sạn, phòng, giá cả, dịch vụ hoặc hotline 1800-9999."
        
        if any(w in msg_lower for w in ["wifi", "internet", "mạng"]):
            return "📶 Tất cả InterContinental đều có WiFi miễn phí tốc độ cao cho khách lưu trú."
        
        return fallback_reply()

# ========== HÀM MỚI CÓ MEMORY ==========
def generate_reply_with_memory(message: str, user_id: str = "default") -> str:
    """Phiên bản mới có memory - SỬA LỖI MATCH NHẦM VÀ THÊM XỬ LÝ DỊCH VỤ"""
    msg = message.lower().strip()
    
    # ========== QUAN TRỌNG: XỬ LÝ DỊCH VỤ TRƯỚC ==========
    # 1. Xử lý DỊCH VỤ SPA (kể cả khi gõ sai "sọa")
    spa_keywords = ["spa", "sọa", "massage", "mát xa", "thư giãn", "xông hơi"]
    if any(keyword in msg for keyword in spa_keywords):
        response = """💆 **Dịch vụ Spa & Massage tại InterContinental:**
• Massage thư giãn: 600,000 VND/60 phút
• Massage trị liệu: 800,000 VND/60 phút  
• Gói Spa cao cấp: 1,200,000 VND/90 phút (bao gồm massage + xông hơi)
• Xông hơi riêng: 150,000 VND/người
⏰ Thời gian: 9:00 - 21:00 hàng ngày
📞 Đặt lịch trước qua hotline: 1800-9999"""
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # 2. Xử lý DỊCH VỤ ẨM THỰC
    food_keywords = ["ăn uống", "nhà hàng", "buffet", "đồ ăn", "thức ăn", "bbq", "tiệc"]
    if any(keyword in msg for keyword in food_keywords):
        response = """🍽️ **Dịch vụ Ẩm thực tại InterContinental:**
• Buffet sáng: 250,000 VND/người (6:00-10:00)
• Nhà hàng à la carte: 500,000 - 1,500,000 VND/người (10:00-22:00)
• Quầy bar: 150,000 - 300,000 VND/đồ uống (16:00-23:00)
• Tiệc BBQ hải sản: 800,000 VND/người (18:00-22:00)
• Tiệc cưới/Event: 5,000,000 VND trở lên (tùy quy mô)
📞 Đặt bàn qua hotline: 1800-9999"""
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # 3. Xử lý GIÁ PHÒNG CỤ THỂ THEO ĐỊA ĐIỂM
    if any(word in msg for word in ["giá", "price", "bao nhiêu", "bao nhiêu tiền", "chi phí"]):
        # Danh sách thành phố
        cities = {
            "hà nội": {"đơn": "1.8 triệu", "đôi": "3 triệu", "vip": "6 triệu", "address": "1 Lê Thánh Tông, Hoàn Kiếm"},
            "đà nẵng": {"đơn": "1.5 triệu", "đôi": "2.5 triệu", "vip": "5 triệu", "address": "Bãi biển Mỹ Khê"},
            "nha trang": {"đơn": "1.6 triệu", "đôi": "2.8 triệu", "vip": "5.5 triệu", "address": "2 Trần Phú"},
            "đà lạt": {"đơn": "1.3 triệu", "đôi": "2.2 triệu", "vip": "4.5 triệu", "address": "Đồi Cù"},
            "hồ chí minh": {"đơn": "2 triệu", "đôi": "3.5 triệu", "vip": "7 triệu", "address": "Bitexco Tower Q1"},
            "hcm": {"đơn": "2 triệu", "đôi": "3.5 triệu", "vip": "7 triệu", "address": "Bitexco Tower Q1"},
            "sài gòn": {"đơn": "2 triệu", "đôi": "3.5 triệu", "vip": "7 triệu", "address": "Bitexco Tower Q1"},
            "thanh hóa": {"đơn": "1.8 triệu", "đôi": "3.6 triệu", "vip": "7 triệu", "address": "Bãi biển Sầm Sơn"}
        }
        
        # Tìm thành phố
        found_city = None
        city_data = None
        for city, data in cities.items():
            if city in msg:
                found_city = city
                city_data = data
                break
        
        if found_city:
            city_name = found_city.upper() if found_city in ["hà nội", "đà nẵng", "nha trang", "đà lạt", "thanh hóa"] else found_city.title()
            
            # Xác định loại phòng
            if "đơn" in msg:
                response = f"🛏️ **Phòng Đơn tại InterContinental {city_name}:** {city_data['đơn']} VND/đêm\n📍 {city_data['address']}\n📞 Đặt phòng: 1800-9999"
            elif "đôi" in msg or "đối" in msg:  # Xử lý lỗi chính tả "đối"
                response = f"🛏️ **Phòng Đôi tại InterContinental {city_name}:** {city_data['đôi']} VND/đêm\n📍 {city_data['address']}\n📞 Đặt phòng: 1800-9999"
            elif "vip" in msg:
                response = f"🛏️ **Phòng VIP tại InterContinental {city_name}:** {city_data['vip']} VND/đêm\n📍 {city_data['address']}\n📞 Đặt phòng: 1800-9999"
            else:
                response = f"💰 **Giá phòng tại InterContinental {city_name}:**\n• Phòng Đơn: {city_data['đơn']} VND/đêm\n• Phòng Đôi: {city_data['đôi']} VND/đêm\n• Phòng VIP: {city_data['vip']} VND/đêm\n📍 {city_data['address']}\n📞 Hotline: 1800-9999"
            
            _add_to_history(user_id, "user", message)
            _add_to_history(user_id, "assistant", response)
            return response
    
    # 4. Quick responses CHÍNH XÁC
    # Hotline
    if any(w in msg for w in ["hotline", "số điện thoại", "liên hệ", "điện thoại", "gọi điện"]):
        response = "📞 Hotline đặt phòng & dịch vụ 24/7: 1800-9999"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # Cảm ơn
    if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
        response = "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # Câu chào - CHỈ khi câu rất ngắn
    if len(msg.split()) <= 3:
        exact_greetings = ["xin chào", "hello", "hi ", "chào bạn", "chào anh", "chào chị", "chào em"]
        for greeting in exact_greetings:
            if msg.startswith(greeting) or msg == greeting.replace(" ", ""):
                response = "Xin chào! Tôi là trợ lý ảo MelMaybe. Tôi có thể giúp gì cho bạn?"
                _add_to_history(user_id, "user", message)
                _add_to_history(user_id, "assistant", response)
                return response
    
    # 5. Basic info
    if any(w in msg for w in ["khách sạn", "hotel", "chi nhánh", "ở đâu", "có ở đâu"]):
        response = "🏨 **Hệ thống InterContinental Việt Nam (6 khách sạn 5 sao):**\n• Hà Nội: 1 Lê Thánh Tông, Hoàn Kiếm\n• Đà Nẵng: Bãi biển Mỹ Khê\n• Nha Trang: 2 Trần Phú\n• Đà Lạt: Đồi Cù\n• TP.HCM: Bitexco Tower Q1\n• Thanh Hóa: Bãi biển Sầm Sơn\n📞 Hotline: 1800-9999"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # 6. Loại phòng chung
    if "phòng đơn" in msg:
        response = "🛏️ **Phòng Đơn:** Giá từ 1.3 - 2 triệu VND/đêm\n📍 Chi tiết theo khách sạn:\n• Hà Nội: 1.8tr\n• Đà Nẵng: 1.5tr\n• Nha Trang: 1.6tr\n• Đà Lạt: 1.3tr\n• TP.HCM: 2tr\n• Thanh Hóa: 1.8tr\n📞 Hotline: 1800-9999"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    if "phòng đôi" in msg or "phòng đối" in msg:  # Xử lý lỗi chính tả
        response = "🛏️ **Phòng Đôi:** Giá từ 2.2 - 3.6 triệu VND/đêm\n📍 Chi tiết theo khách sạn:\n• Hà Nội: 3tr\n• Đà Nẵng: 2.5tr\n• Nha Trang: 2.8tr\n• Đà Lạt: 2.2tr\n• TP.HCM: 3.5tr\n• Thanh Hóa: 3.6tr\n📞 Hotline: 1800-9999"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    if "phòng vip" in msg:
        response = "🛏️ **Phòng VIP:** Giá từ 4.5 - 7 triệu VND/đêm\n📍 Chi tiết theo khách sạn:\n• Hà Nội: 6tr\n• Đà Nẵng: 5tr\n• Nha Trang: 5.5tr\n• Đà Lạt: 4.5tr\n• TP.HCM: 7tr\n• Thanh Hóa: 7tr\n📞 Hotline: 1800-9999"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # 7. Dùng AI cho các câu hỏi còn lại
    response = _safe_groq_reply(message)
    
    # Lưu vào history
    _add_to_history(user_id, "user", message)
    _add_to_history(user_id, "assistant", response)
    
    return response

# ========== HÀM CŨ VẪN ĐƯỢC GIỮ ĐỂ TƯƠNG THÍCH ==========
def generate_reply(message: str) -> str:
    """Hàm cũ - tương thích ngược"""
    return generate_reply_with_memory(message, "default_user")

def generate_groq_reply(user_message: str) -> str:
    """Wrapper function cho compatibility"""
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

# ========== HÀM TIỆN ÍCH ==========
def clear_chat_history(user_id: str = "default"):
    """Xóa lịch sử chat của user"""
    _clear_history(user_id)
    print(f"🧹 Cleared chat history for user: {user_id}")

def get_chat_history(user_id: str = "default") -> List[Dict]:
    """Lấy lịch sử chat"""
    return _get_user_history(user_id)

# ========== TEST DỊCH VỤ SPA ==========
if __name__ == "__main__":
    print("🧪 Testing dịch vụ spa...")
    
    test_cases = [
        "dịch vụ sọa giá bao nhiêu",  # Lỗi chính tả
        "spa có những gói nào",
        "massage giá thế nào",
        "tôi muốn đi có dịch vụ sọa thì giá thế nào"  # Câu hỏi từ ảnh
    ]
    
    for question in test_cases:
        print(f"\n{'='*60}")
        print(f"User: {question}")
        response = generate_reply(question)
        print(f"Bot: {response}")
