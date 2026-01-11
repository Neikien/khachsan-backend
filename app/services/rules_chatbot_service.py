import os
import logging
from typing import List, Dict
from openai import OpenAI

logger = logging.getLogger(__name__)

# ========== BỘ NHỚ HỘI THOẠI ĐƠN GIẢN ==========
# Lưu trữ lịch sử hội thoại theo user_id
conversation_memory: Dict[str, List[Dict]] = {}

def get_conversation_history(user_id: str = "default") -> List[Dict]:
    """Lấy lịch sử hội thoại của user"""
    return conversation_memory.get(user_id, [])

def add_to_conversation(user_id: str = "default", 
                       role: str = "user", 
                       content: str = ""):
    """Thêm tin nhắn vào lịch sử"""
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []
    
    # Giới hạn lịch sử để không quá dài (giữ 10 tin nhắn gần nhất)
    if len(conversation_memory[user_id]) >= 20:  # 10 cặp user-bot
        conversation_memory[user_id] = conversation_memory[user_id][-18:]
    
    conversation_memory[user_id].append({
        "role": role,
        "content": content
    })

def clear_conversation(user_id: str = "default"):
    """Xóa lịch sử hội thoại"""
    if user_id in conversation_memory:
        conversation_memory[user_id] = []

# ========== CHATBOT CÓ MEMORY ==========
def generate_reply_with_memory(message: str, user_id: str = "default") -> str:
    """Chatbot có nhớ context hội thoại"""
    msg = message.lower().strip()
    
    # 1. Thêm tin nhắn user vào history
    add_to_conversation(user_id, "user", message)
    
    # 2. Lấy lịch sử hội thoại
    history = get_conversation_history(user_id)
    
    # 3. Kiểm tra quick responses (vẫn giữ để tăng tốc)
    if any(w in msg for w in ["hotline", "số điện thoại", "liên hệ"]):
        response = "📞 Hotline đặt phòng 24/7: 1800-9999"
        add_to_conversation(user_id, "assistant", response)
        return response
    
    if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
        response = "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
        add_to_conversation(user_id, "assistant", response)
        return response
    
    # 4. Xử lý bằng AI với context
    try:
        response = _safe_groq_reply_with_context(message, history)
        add_to_conversation(user_id, "assistant", response)
        return response
    except Exception as e:
        logger.error(f"AI error: {e}")
        response = "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại!"
        add_to_conversation(user_id, "assistant", response)
        return response

def _safe_groq_reply_with_context(user_message: str, history: List[Dict]) -> str:
    """AI với context hội thoại"""
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("apikey")
    
    if not api_key:
        return emergency_fallback(user_message)
    
    system_prompt = """BẠN LÀ TRỢ LÝ ẢO MELMAYBE - HỆ THỐNG 6 KHÁCH SẠN 5 SAO:

=== THÔNG TIN QUAN TRỌNG ===
• 6 khách sạn: Hà Nội, Đà Nẵng, Nha Trang, Đà Lạt, TP.HCM, Thanh Hóa
• Hotline: 1800-9999
• Giá phòng: Hà Nội (Đơn 1.8tr, Đôi 3tr, VIP 6tr), Đà Nẵng (1.5tr, 2.5tr, 5tr), etc.

=== QUY TẮC ===
1. LUÔN nhớ context cuộc trò chuyện trước đó
2. Nếu user hỏi tiếp theo, trả lời có liên kết với câu trước
3. Trả lời ngắn gọn, thân thiện bằng tiếng Việt
4. Dùng đúng thông tin trên, không bịa
5. Nhắc hotline khi cần thiết"""
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Tạo messages từ: system prompt + history + câu hỏi mới
        messages = [{"role": "system", "content": system_prompt}]
        
        # Thêm lịch sử hội thoại (chỉ lấy 8 tin nhắn gần nhất để tiết kiệm token)
        recent_history = history[-8:] if len(history) > 8 else history
        messages.extend(recent_history)
        
        # Thêm câu hỏi hiện tại (đã có trong history, nhưng cần thêm vào messages)
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=250,
            timeout=20.0
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI Error: {e}")
        return emergency_fallback(user_message)

# ========== API TƯƠNG THÍCH NGƯỢC ==========
def generate_reply(message: str) -> str:
    """Wrapper để tương thích với code cũ (dùng user mặc định)"""
    return generate_reply_with_memory(message, "default_user")

def emergency_fallback(message: str) -> str:
    msg = message.lower()
    if "hotline" in msg:
        return "📞 Hotline: 1800-9999"
    return "Xin lỗi, hệ thống đang bận. Vui lòng gọi 1800-9999 để được hỗ trợ."
