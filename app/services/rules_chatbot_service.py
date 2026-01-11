import os
import logging
import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from openai import OpenAI

logger = logging.getLogger(__name__)

# ========== BỘ NHỚ HỘI THOẠI MẠNH HƠN ==========
class ConversationMemory:
    """Quản lý bộ nhớ hội thoại mạnh mẽ"""
    
    def __init__(self, max_messages=10, max_tokens_context=2000):
        self.memories = defaultdict(list)  # user_id -> list of messages
        self.contexts = defaultdict(dict)   # user_id -> context dict
        self.max_messages = max_messages
        self.max_tokens_context = max_tokens_context
    
    def add_message(self, user_id: str, role: str, content: str):
        """Thêm tin nhắn vào memory"""
        self.memories[user_id].append({
            "role": role,
            "content": content,
            "timestamp": logging.getLogger(__name__).info
        })
        
        # Giới hạn số tin nhắn
        if len(self.memories[user_id]) > self.max_messages:
            self.memories[user_id] = self.memories[user_id][-self.max_messages:]
    
    def get_conversation_context(self, user_id: str) -> str:
        """Tạo context string từ toàn bộ hội thoại"""
        if user_id not in self.memories or not self.memories[user_id]:
            return ""
        
        # Tóm tắt thông tin quan trọng từ hội thoại
        context_lines = []
        
        # Phân tích hội thoại để trích xuất thông tin quan trọng
        important_info = self._extract_important_info(user_id)
        
        if important_info:
            context_lines.append("=== THÔNG TIN ĐÃ TRAO ĐỔI TRƯỚC ĐÓ ===")
            for key, value in important_info.items():
                context_lines.append(f"• {key}: {value}")
            context_lines.append("")
        
        # Thêm các tin nhắn gần nhất
        recent_msgs = self.memories[user_id][-6:]  # 6 tin nhắn gần nhất
        if recent_msgs:
            context_lines.append("=== CUỘC HỘI THOẠI GẦN ĐÂY ===")
            for msg in recent_msgs:
                role_display = "Khách" if msg["role"] == "user" else "Trợ lý"
                content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                context_lines.append(f"{role_display}: {content_preview}")
        
        return "\n".join(context_lines)
    
    def _extract_important_info(self, user_id: str) -> Dict[str, str]:
        """Trích xuất thông tin quan trọng từ hội thoại"""
        info = {}
        
        if user_id not in self.memories:
            return info
        
        # Lấy toàn bộ hội thoại
        conversation = self.memories[user_id]
        
        # Tìm số người
        people_count = self._find_people_count(conversation)
        if people_count:
            info["Số người"] = f"{people_count} người"
        
        # Tìm địa điểm
        location = self._find_location(conversation)
        if location:
            info["Địa điểm quan tâm"] = location
        
        # Tìm loại phòng
        room_type = self._find_room_type(conversation)
        if room_type:
            info["Loại phòng quan tâm"] = room_type
        
        # Tìm số ngày
        days = self._find_stay_days(conversation)
        if days:
            info["Số ngày lưu trú"] = f"{days} ngày"
        
        return info
    
    def _find_people_count(self, conversation: List[Dict]) -> Optional[int]:
        """Tìm số người được nhắc đến trong hội thoại"""
        for msg in conversation[::-1]:  # Duyệt từ mới đến cũ
            if msg["role"] == "user":
                text = msg["content"].lower()
                # Tìm các pattern về số người
                patterns = [
                    r'(\d+)\s*người',
                    r'còn\s*(\d+)\s*người',
                    r'thêm\s*(\d+)\s*người',
                    r'(\d+)\s*người nữa',
                    r'nhóm\s*(\d+)\s*người',
                    r'(\d+)\s*người trong nhóm',
                    r'tôi có\s*(\d+)\s*người',
                ]
                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            return int(match.group(1))
                        except:
                            pass
        return None
    
    def _find_location(self, conversation: List[Dict]) -> Optional[str]:
        """Tìm địa điểm được nhắc đến"""
        locations = ["hà nội", "đà nẵng", "nha trang", "đà lạt", "hồ chí minh", "hcm", "sài gòn", "thanh hóa"]
        for msg in conversation[::-1]:
            if msg["role"] == "user":
                text = msg["content"].lower()
                for loc in locations:
                    if loc in text:
                        return loc.title() if loc in ["hà nội", "đà nẵng", "nha trang", "đà lạt", "thanh hóa"] else loc.upper()
        return None
    
    def _find_room_type(self, conversation: List[Dict]) -> Optional[str]:
        """Tìm loại phòng được nhắc đến"""
        room_types = ["phòng đơn", "phòng đôi", "phòng vip", "single", "double", "vip", "suite"]
        for msg in conversation[::-1]:
            if msg["role"] == "user":
                text = msg["content"].lower()
                for room in room_types:
                    if room in text:
                        if "đơn" in room or "single" in room:
                            return "Phòng Đơn"
                        elif "đôi" in room or "double" in room:
                            return "Phòng Đôi"
                        elif "vip" in room or "suite" in room:
                            return "Phòng VIP"
        return None
    
    def _find_stay_days(self, conversation: List[Dict]) -> Optional[int]:
        """Tìm số ngày lưu trú"""
        for msg in conversation[::-1]:
            if msg["role"] == "user":
                text = msg["content"].lower()
                match = re.search(r'(\d+)\s*ngày', text)
                if match:
                    try:
                        return int(match.group(1))
                    except:
                        pass
        return None
    
    def clear_memory(self, user_id: str):
        """Xóa memory của user"""
        if user_id in self.memories:
            del self.memories[user_id]
        if user_id in self.contexts:
            del self.contexts[user_id]

# Khởi tạo memory system
memory = ConversationMemory(max_messages=12)

# ========== HÀM CHÍNH VỚI MEMORY MẠNH ==========
def generate_reply_with_memory(message: str, user_id: str = "default") -> str:
    """Phiên bản mới với memory mạnh - LUÔN NHỚ CONTEXT"""
    msg = message.lower().strip()
    
    # 1. Thêm tin nhắn user vào memory TRƯỚC KHI xử lý
    memory.add_message(user_id, "user", message)
    
    # 2. Lấy context từ toàn bộ hội thoại
    conversation_context = memory.get_conversation_context(user_id)
    
    # 3. Quick responses (chỉ cho những câu cực kỳ đơn giản)
    if _is_simple_greeting(msg):
        response = "Xin chào! Tôi là trợ lý ảo MelMaybe. Tôi có thể giúp gì cho bạn về khách sạn InterContinental?"
        memory.add_message(user_id, "assistant", response)
        return response
    
    if "hotline" in msg or "số điện thoại" in msg:
        response = "📞 Hotline đặt phòng & dịch vụ 24/7: 1800-9999"
        memory.add_message(user_id, "assistant", response)
        return response
    
    if "cảm ơn" in msg or "thanks" in msg:
        response = "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
        memory.add_message(user_id, "assistant", response)
        return response
    
    # 4. Dùng AI VỚI TOÀN BỘ CONTEXT
    try:
        response = _safe_groq_reply_with_full_context(message, user_id, conversation_context)
    except Exception as e:
        logger.error(f"AI error: {e}")
        response = _fallback_based_on_context(message, conversation_context)
    
    # 5. Lưu phản hồi vào memory
    memory.add_message(user_id, "assistant", response)
    
    return response

def _is_simple_greeting(msg: str) -> bool:
    """Kiểm tra xem có phải là câu chào đơn giản không"""
    greetings = ["xin chào", "hello", "hi ", "chào bạn", "chào anh", "chào chị"]
    for greeting in greetings:
        if msg.startswith(greeting) and len(msg.split()) <= 4:
            return True
    return False

def _safe_groq_reply_with_full_context(user_message: str, user_id: str, conversation_context: str) -> str:
    """AI với TOÀN BỘ context hội thoại"""
    api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return _fallback_based_on_context(user_message, conversation_context)
    
    # BASE SYSTEM PROMPT với thông tin khách sạn
    base_system_prompt = """BẠN LÀ TRỢ LÝ ẢO MELMAYBE - HỆ THỐNG INTERCONTINENTAL VIỆT NAM

=== THÔNG TIN KHÁCH SẠN (6 khách sạn 5 sao) ===
1. HÀ NỘI: 1 Lê Thánh Tông, Hoàn Kiếm
2. ĐÀ NẴNG: Bãi biển Mỹ Khê  
3. NHA TRANG: 2 Trần Phú
4. ĐÀ LẠT: Đồi Cù
5. TP.HCM: Bitexco Tower Q1
6. THANH HÓA: Bãi biển Sầm Sơn

=== GIÁ PHÒNG (triệu VND/đêm) ===
• HÀ NỘI: Đơn 1.8, Đôi 3, VIP 6
• ĐÀ NẴNG: Đơn 1.5, Đôi 2.5, VIP 5
• NHA TRANG: Đơn 1.6, Đôi 2.8, VIP 5.5
• ĐÀ LẠT: Đơn 1.3, Đôi 2.2, VIP 4.5
• TP.HCM: Đơn 2, Đôi 3.5, VIP 7
• THANH HÓA: Đơn 1.8, Đôi 3.6, VIP 7

=== DỊCH VỤ ===
• Spa: 600,000 - 1,200,000 VND
• Buffet sáng: 250,000 VND
• Nhà hàng: 500,000 - 1,500,000 VND
• Gym/Bể bơi: Miễn phí cho khách
• Hotline: 1800-9999"""

    # Tạo full system prompt với conversation context
    if conversation_context:
        full_system_prompt = f"""{base_system_prompt}

=== CONTEXT HỘI THOẠI HIỆN TẠI ===
{conversation_context}

=== QUY TẮC QUAN TRỌNG ===
1. LUÔN ĐỌC KỸ context trên trước khi trả lời
2. Nếu khách đã nói về thông tin trước đó (số người, địa điểm, ngày...), PHẢI sử dụng thông tin đó
3. Trả lời có tính kế thừa, liên kết với những gì đã nói trước
4. Nếu khách hỏi tiếp theo về chủ đề cũ, hiểu đó là tiếp nối cuộc trò chuyện
5. Trả lời bằng tiếng Việt, thân thiện, tự nhiên như đang trò chuyện
6. Nhắc hotline 1800-9999 khi cần đặt phòng/dịch vụ"""
    else:
        full_system_prompt = f"""{base_system_prompt}

=== QUY TẮC ===
1. Trả lời bằng tiếng Việt, thân thiện
2. Nhắc hotline 1800-9999 khi cần
3. Hỏi thêm thông tin nếu cần thiết"""
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Lấy lịch sử tin nhắn gần nhất (không bao gồm system prompt)
        recent_messages = memory.memories.get(user_id, [])[-8:]  # 8 tin nhắn gần nhất
        
        # Tạo messages array
        messages = [{"role": "system", "content": full_system_prompt}]
        
        # Thêm recent messages (đã bao gồm câu hỏi hiện tại)
        for msg in recent_messages:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        print(f"\n🧠 DEBUG: Sending to AI with {len(recent_messages)} previous messages")
        print(f"📝 Context: {conversation_context[:200]}...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=350,
            timeout=25.0
        )
        
        reply = response.choices[0].message.content
        print(f"✅ AI Reply: {reply[:150]}...")
        
        return reply
        
    except Exception as e:
        print(f"💥 AI Error: {e}")
        raise

def _fallback_based_on_context(user_message: str, conversation_context: str) -> str:
    """Fallback dựa trên context khi AI không hoạt động"""
    msg = user_message.lower()
    
    # Nếu có context, cố gắng trả lời dựa trên đó
    if conversation_context:
        # Kiểm tra xem đang nói về số người không
        if "số người" in conversation_context.lower():
            match = re.search(r'Số người:\s*(\d+)', conversation_context)
            if match:
                people = int(match.group(1))
                return f"Hiện tôi nhớ bạn đang có {people} người. Vui lòng gọi hotline 1800-9999 để được tư vấn chi tiết về phòng cho {people} người."
    
    # Fallback chung
    if "spa" in msg or "sọa" in msg:
        return "💆 Dịch vụ Spa: 600,000 - 1,200,000 VND. Hotline: 1800-9999"
    
    if "giá" in msg or "bao nhiêu" in msg:
        return "💰 Giá phòng từ 1.3 - 7 triệu VND/đêm tùy địa điểm và loại phòng. Hotline: 1800-9999"
    
    return """🏨 **Xin chào! Tôi là trợ lý ảo InterContinental.**

Hiện hệ thống AI đang bận. Vui lòng:
• Gọi hotline 1800-9999 để được hỗ trợ ngay
• Hoặc nhắn lại câu hỏi của bạn"""

# ========== HÀM CŨ VẪN TƯƠNG THÍCH ==========
def generate_reply(message: str) -> str:
    """Hàm cũ - tương thích ngược (dùng memory)"""
    return generate_reply_with_memory(message, "default_user")

def generate_groq_reply(user_message: str) -> str:
    """Wrapper function cho compatibility"""
    return _safe_groq_reply(user_message)

def _safe_groq_reply(user_message: str) -> str:
    """Hàm cũ cho compatibility"""
    api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
    if not api_key:
        return fallback_reply()
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý khách sạn InterContinental. Hotline: 1800-9999"},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        return response.choices[0].message.content
    except:
        return fallback_reply()

def fallback_reply() -> str:
    return """🏨 **Xin chào! Tôi là trợ lý ảo InterContinental.**

Tôi có thể giúp bạn:
• Tư vấn phòng theo số người
• Giá phòng chi tiết 6 khách sạn
• Dịch vụ: spa, ẩm thực, tiệc
• Hotline: 1800-9999

Bạn muốn hỏi về điều gì ạ?"""

# ========== HÀM TIỆN ÍCH ==========
def clear_chat_history(user_id: str = "default"):
    """Xóa lịch sử chat"""
    memory.clear_memory(user_id)
    print(f"🧹 Đã xóa lịch sử chat của user: {user_id}")

def get_chat_summary(user_id: str = "default") -> str:
    """Lấy tóm tắt hội thoại"""
    return memory.get_conversation_context(user_id)

# ========== TEST VỚI ĐOẠN CHAT CỦA BẠN ==========
if __name__ == "__main__":
    print("🧪 Testing với đoạn chat thực tế...")
    print("="*70)
    
    test_conversation = [
        "Xin chào",
        "tôi còn 3 người",
        "vậy option đặt phòng nào ok",
        "giờ tôi rủ được thêm 3 người nữa",
        "vậy option đặt phòng nào ok nhất cho nhóm của tôi khi đi trong 6 ngày"
    ]
    
    for i, question in enumerate(test_conversation):
        print(f"\n👤 [Lần {i+1}] User: {question}")
        
        # Xem context hiện tại
        context_before = get_chat_summary("test_user")
        if context_before:
            print(f"📊 Context trước: {context_before[:100]}...")
        
        # Get response
        response = generate_reply_with_memory(question, "test_user")
        print(f"🤖 Bot: {response}")
        
        # Xem context sau
        print(f"💾 Memory: {len(memory.memories.get('test_user', []))} messages stored")
    
    print("\n" + "="*70)
    print("📋 Tóm tắt hội thoại cuối cùng:")
    print(get_chat_summary("test_user"))
