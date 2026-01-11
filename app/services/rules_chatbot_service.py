import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ConversationSession:
    user_id: str
    messages: List[Dict]
    created_at: float
    last_activity: float
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Kiểm tra session có hết hạn chưa (30 phút không hoạt động)"""
        return time.time() - self.last_activity > timeout_minutes * 60
    
    def update_activity(self):
        """Cập nhật thời gian hoạt động cuối"""
        self.last_activity = time.time()
    
    def add_message(self, role: str, content: str):
        """Thêm tin nhắn vào session"""
        self.messages.append({"role": role, "content": content})
        self.update_activity()
        
        # Giới hạn lịch sử (giữ 12 tin nhắn gần nhất)
        if len(self.messages) > 12:
            self.messages = self.messages[-12:]

class ConversationManager:
    """Quản lý nhiều session hội thoại"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
    
    def get_session(self, user_id: str) -> ConversationSession:
        """Lấy hoặc tạo session mới"""
        self.cleanup_expired()
        
        if user_id not in self.sessions:
            self.sessions[user_id] = ConversationSession(
                user_id=user_id,
                messages=[],
                created_at=time.time(),
                last_activity=time.time()
            )
        
        return self.sessions[user_id]
    
    def cleanup_expired(self):
        """Dọn dẹp session đã hết hạn"""
        expired_ids = [
            user_id for user_id, session in self.sessions.items()
            if session.is_expired()
        ]
        for user_id in expired_ids:
            del self.sessions[user_id]
    
    def clear_session(self, user_id: str):
        """Xóa session của user"""
        if user_id in self.sessions:
            del self.sessions[user_id]

# Sử dụng
conv_manager = ConversationManager()

def generate_reply_with_session(message: str, user_id: str = "default") -> str:
    """Chatbot với session management"""
    # Lấy session của user
    session = conv_manager.get_session(user_id)
    
    # Thêm tin nhắn user vào session
    session.add_message("user", message)
    
    # Xử lý với AI có context
    try:
        response = _get_ai_response_with_context(message, session.messages)
        session.add_message("assistant", response)
        return response
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại!"

def _get_ai_response_with_context(user_message: str, history: List[Dict]) -> str:
    """Gọi AI với context từ history"""
    # ... tương tự như trên ...
    pass
