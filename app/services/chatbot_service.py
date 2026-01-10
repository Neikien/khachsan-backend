import os
import logging

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
    
    def sync_generate_reply(self, user_message: str) -> str:
        """Simple synchronous reply without async issues"""
        msg = user_message.lower().strip()
        
        if any(w in msg for w in ["khách sạn", "hotel", "chi nhánh", "cơ sở", "ở đâu"]):
            return "Hệ thống MelMaybe có 5 khách sạn 5 sao tại:\n• Hà Nội: 1 Lê Thánh Tông, Hoàn Kiếm\n• Đà Nẵng: Bãi biển Mỹ Khê\n• Nha Trang: 2 Trần Phú\n• Đà Lạt: Đồi Cù, phường 1\n• TP.HCM: Bitexco Financial Tower, Quận 1"
        
        if any(w in msg for w in ["phòng đơn", "đơn"]):
            return "Phòng Đơn: 1.5 - 2 triệu VND/đêm (tùy địa điểm)"
        
        if any(w in msg for w in ["phòng đôi", "đôi"]):
            return "Phòng Đôi: 2.5 - 3 triệu VND/đêm"
        
        if any(w in msg for w in ["phòng vip", "vip"]):
            return "Phòng VIP: 5 triệu VND/đêm"
        
        if any(w in msg for w in ["phòng", "giá", "đặt phòng", "room", "price", "bao nhiêu"]):
            return "Giá phòng:\n• Phòng Đơn: 1.5-2 triệu\n• Phòng Đôi: 2.5-3 triệu\n• Phòng VIP: 5 triệu\nHotline đặt phòng: 1800-9999"
        
        if any(w in msg for w in ["hotline", "liên hệ", "số điện thoại", "điện thoại"]):
            return "📞 Hotline hỗ trợ 24/7: 1800-9999"
        
        if any(w in msg for w in ["cảm ơn", "thanks", "thank you"]):
            return "Cảm ơn bạn! Chúc bạn một ngày tốt lành! 😊"
        
        if any(w in msg for w in ["chào", "hello", "hi", "xin chào"]):
            return "Xin chào! Tôi là trợ lý ảo MelMaybe. Tôi có thể giúp bạn:\n• Tìm thông tin khách sạn\n• Tư vấn giá phòng\n• Hỗ trợ đặt phòng\n• Cung cấp hotline liên hệ\nBạn cần hỗ trợ gì ạ?"
        
        return "Tôi có thể giúp bạn tìm thông tin khách sạn, giá phòng, đặt phòng hoặc cung cấp hotline liên hệ. Bạn muốn hỏi về điều gì cụ thể?"

    def _fallback_reply(self, user_message: str) -> str:
        """Legacy fallback"""
        return self.sync_generate_reply(user_message)

chatbot_service = ChatbotService()
