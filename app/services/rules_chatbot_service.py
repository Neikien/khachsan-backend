import os
import logging
from typing import Dict, List
from collections import defaultdict
from openai import OpenAI  # Import ở cấp module

logger = logging.getLogger(__name__)

# ========== BỘ NHỚ HỘI THOẠI ==========
# Lưu trữ lịch sử hội thoại cho từng user
_conversation_history: Dict[str, List[Dict]] = defaultdict(list)
_MAX_HISTORY_LENGTH = 6  # Chỉ nhớ 6 tin nhắn gần nhất (3 cặp Q-A)

def _get_user_history(user_id: str = "default") -> List[Dict]:
    """Lấy lịch sử hội thoại của user"""
    return _conversation_history.get(user_id, [])

def _add_to_history(user_id: str = "default", role: str = "user", content: str = ""):
    """Thêm tin nhắn vào lịch sử"""
    history = _conversation_history[user_id]
    history.append({"role": role, "content": content})
    
    # Giới hạn độ dài lịch sử
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
2. Không biết → "Hiện chưa có thông tin về...", có thể trả lời khéo léo một chút, ko quá máy móc
3. Có thể gợi ý khách hàng về các địa điểm mà ta có khách sạn một cách đơn giản.
4. Nhắc hotline 1800-9999 để đặt phòng/dịch vụ
5. Trả lời bằng tiếng Việt, ngắn gọn, thân thiện
6. Với dịch vụ: nêu giá và thời gian phục vụ
7. Với liên hệ: cung cấp số quản lý tương ứng, nhắc đến quản lý là phải đi kèm với số điện thoại
8. Không nhắc đến giá và mã khách sạn trừ khi khách hỏi
9. Khi nhận được câu hỏi, hãy xem thật kĩ xem thông tin có thể liên quan đến khu vực được hỏi hay không, xem xét kĩ r mới nhận định thông tin có liên quan đến mong muốn du lịch không"""
    
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

# ========== HÀM MỚI CÓ MEMORY ==========
def _safe_groq_reply_with_context(user_message: str, user_id: str = "default") -> str:
    """Phiên bản AI có nhớ context hội thoại"""
    print("\n" + "="*60)
    print("🧠 AI WITH CONVERSATION MEMORY")
    
    api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ No API key, using fallback")
        return fallback_reply()
    
    # Lấy lịch sử hội thoại
    history = _get_user_history(user_id)
    
    # Tạo system prompt với hướng dẫn về memory
    system_prompt = """BẠN LÀ TRỢ LÝ ẢO MELMAYBE - HỆ THỐNG 6 KHÁCH SẠN 5 SAO:

=== THÔNG TIN CHÍNH ===
KHÁCH SẠN:
1. InterContinental HÀ NỘI (291): 1 Lê Thánh Tông, Hoàn Kiếm - Quản lý: Nguyễn Văn Toàn (0909123456)
2. InterContinental ĐÀ NẴNG (432): Bãi biển Mỹ Khê - Quản lý: Trần Thị Hương (0918234567)
3. InterContinental NHA TRANG (493): 2 Trần Phú - Quản lý: Lê Minh Tuấn (0927345678) - Biết tiếng Anh/Nhật
4. InterContinental ĐÀ LẠT (684): Đồi Cù - Quản lý: Phạm Thị Lan (0936456789) - Chuyên honeymoon
5. InterContinental TP.HCM (795): Bitexco Tower Q1 - Quản lý: Hoàng Văn Đức (0945567890)
6. InterContinental THANH HÓA (366): Bãi biển Sầm Sơn - Quản lý: Nguyễn Thị Mai(0912345678')

GIÁ PHÒNG (VND/đêm):
• HÀ NỘI: Đơn 1.8tr, Đôi 3tr, VIP 6tr
• ĐÀ NẴNG: Đơn 1.5tr, Đôi 2.5tr, VIP 5tr
• NHA TRANG: Đơn 1.6tr, Đôi 2.8tr, VIP 5.5tr
• ĐÀ LẠT: Đơn 1.3tr, Đôi 2.2tr, VIP 4.5tr
• TP.HCM: Đơn 2tr, Đôi 3.5tr, VIP 7tr
• THANH HÓA: Đơn 1.8tr, Đôi 3.6tr, VIP 7tr

HOTLINE: 1800-9999

=== QUY TẮC QUAN TRỌNG ===
1. LUÔN NHỚ cuộc hội thoại trước đó. Nếu user hỏi tiếp về chủ đề cũ, hãy trả lời có liên kết.
2. CHỈ dùng thông tin trên, KHÔNG bịa ra
3. Trả lời bằng tiếng Việt, ngắn gọn, thân thiện
4. Nhắc hotline 1800-9999 khi cần đặt phòng/dịch vụ
5. Với câu hỏi tiếp theo: Hiểu ngữ cảnh và trả lời phù hợp

Ví dụ: 
- Nếu user trước hỏi về Hà Nội, sau hỏi "Giá bao nhiêu?" → Hiểu là hỏi giá Hà Nội
- Nếu user hỏi "Có phòng không?" sau khi đã nói về địa điểm → Hiểu là phòng ở địa điểm đó"""
    
    try:
        print("🤖 Sending to Groq AI with context...")
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Tạo messages: system prompt + history + current question
        messages = [{"role": "system", "content": system_prompt}]
        
        # Thêm lịch sử hội thoại
        messages.extend(history)
        
        # Thêm câu hỏi hiện tại
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=250,
            timeout=20.0
        )
        
        reply = response.choices[0].message.content
        print(f"✅ AI WITH MEMORY SUCCESS! Reply: {reply[:100]}...")
        print("="*60)
        return reply
        
    except Exception as e:
        print(f"💥 AI Error: {type(e).__name__}: {str(e)}")
        logger.error(f"Groq API with context failed: {e}")
        # Fallback về phiên bản không có memory
        return _safe_groq_reply(user_message)

# ========== HÀM CHÍNH MỚI CÓ MEMORY ==========
def generate_reply_with_memory(message: str, user_id: str = "default") -> str:
    """Phiên bản mới có memory - SỬA LỖI MATCH NHẦM"""
    msg = message.lower().strip()
    
    # FIX: Xử lý câu hỏi về GIÁ CỤ THỂ trước tiên (ưu tiên cao nhất)
    # Để tránh bị match nhầm với "chào" trong "bao nhiêu"
    
    # 1. KIỂM TRA CÂU HỎI VỀ GIÁ CỤ THỂ THEO ĐỊA ĐIỂM
    if any(word in msg for word in ["giá", "price", "bao nhiêu", "bao nhiêu tiền", "chi phí"]):
        # Kiểm tra xem có đề cập đến thành phố không
        city_info = ""
        if "hà nội" in msg or "hanoi" in msg:
            city_info = "Hà Nội"
            if "đơn" in msg:
                response = f"🛏️ **Phòng Đơn tại InterContinental {city_info}:** 1.8 triệu VND/đêm\n📍 1 Lê Thánh Tông, Hoàn Kiếm\n📞 Hotline: 1800-9999"
            elif "đôi" in msg:
                response = f"🛏️ **Phòng Đôi tại InterContinental {city_info}:** 3 triệu VND/đêm\n📍 1 Lê Thánh Tông, Hoàn Kiếm\n📞 Hotline: 1800-9999"
            elif "vip" in msg:
                response = f"🛏️ **Phòng VIP tại InterContinental {city_info}:** 6 triệu VND/đêm\n📍 1 Lê Thánh Tông, Hoàn Kiếm\n📞 Hotline: 1800-9999"
            else:
                response = f"💰 **Giá phòng tại InterContinental {city_info}:**\n• Đơn: 1.8tr/đêm\n• Đôi: 3tr/đêm\n• VIP: 6tr/đêm\n📍 1 Lê Thánh Tông, Hoàn Kiếm\n📞 Hotline: 1800-9999"
            
            # Lưu vào history
            _add_to_history(user_id, "user", message)
            _add_to_history(user_id, "assistant", response)
            return response
        
        # Tương tự cho các thành phố khác...
        # (Có thể thêm các thành phố khác ở đây)
    
    # 2. Quick responses CHÍNH XÁC (không bị match nhầm)
    # FIX: Kiểm tra chính xác hơn, tránh match "chào" trong "bao nhiêu"
    
    # Hotline - chỉ khi có từ khóa rõ ràng
    hotline_keywords = ["hotline", "số điện thoại", "liên hệ", "điện thoại", "gọi điện", "gọi cho"]
    if any(keyword in msg for keyword in hotline_keywords):
        response = "📞 Hotline đặt phòng 24/7: 1800-9999"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # Cảm ơn - chỉ khi có từ khóa rõ ràng
    if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
        response = "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
        _add_to_history(user_id, "user", message)
        _add_to_history(user_id, "assistant", response)
        return response
    
    # Câu chào - CHỈ khi câu rất ngắn và bắt đầu bằng từ chào
    # FIX QUAN TRỌNG: Tránh match "chào" trong "bao nhiêu"
    if len(msg.split()) <= 3:  # Câu ngắn (tối đa 3 từ)
        exact_greetings = ["xin chào", "hello", "hi ", "chào bạn", "chào anh", "chào chị", "chào em"]
        for greeting in exact_greetings:
            if msg.startswith(greeting) or msg == greeting.replace(" ", ""):
                response = "Xin chào! Tôi là trợ lý ảo MelMaybe. Tôi có thể giúp gì cho bạn?"
                _add_to_history(user_id, "user", message)
                _add_to_history(user_id, "assistant", response)
                return response
    
    # 3. Dùng AI CÓ MEMORY cho tất cả câu hỏi còn lại
    response = _safe_groq_reply_with_context(message, user_id)
    
    # Lưu vào history
    _add_to_history(user_id, "user", message)
    _add_to_history(user_id, "assistant", response)
    
    return response

# ========== HÀM CŨ VẪN ĐƯỢC GIỮ ĐỂ TƯƠNG THÍCH ==========
def generate_reply(message: str) -> str:
    """
    Hàm cũ - VẪN HOẠT ĐỘNG để tương thích ngược
    Nhưng bây giờ sẽ dùng memory với user mặc định
    """
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

# ========== HÀM TIỆN ÍCH MỚI ==========
def clear_chat_history(user_id: str = "default"):
    """Xóa lịch sử chat của user"""
    _clear_history(user_id)
    print(f"🧹 Cleared chat history for user: {user_id}")

def get_chat_history(user_id: str = "default") -> List[Dict]:
    """Lấy lịch sử chat (cho debug)"""
    return _get_user_history(user_id)

# ========== TEST ==========
if __name__ == "__main__":
    # Test memory
    print("🧪 Testing chatbot with memory...")
    
    test_cases = [
        "Xin chào",
        "Tôi muốn hỏi về khách sạn Hà Nội",
        "Giá phòng đơn ở đó bao nhiêu?",  # Sẽ hiểu "ở đó" là Hà Nội
        "Còn Đà Nẵng thì sao?",
        "Cảm ơn!"
    ]
    
    for i, question in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"User [{i+1}]: {question}")
        response = generate_reply_with_memory(question, "test_user")
        print(f"Bot: {response}")
    
    print(f"\n{'='*50}")
    print("📋 Chat history:")
    history = get_chat_history("test_user")
    for msg in history:
        print(f"{msg['role'].upper()}: {msg['content'][:50]}...")
