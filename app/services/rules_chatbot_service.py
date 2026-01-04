import os
import random
import logging

logger = logging.getLogger(__name__)

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
    """Generate reply with fallback to avoid recursion"""
    msg = message.lower()

    # Check for groq/AI questions first
    if any(w in msg for w in ["groq", "ai", "trí tuệ nhân tạo", "artificial"]):
        return "🤖 Tôi sử dụng Groq AI để trả lời các câu hỏi phức tạp về khách sạn!"

    if any(w in msg for w in ["đi đâu", "địa điểm", "du lịch", "tham quan", "nên đi"]):
        return random.choice(SUGGESTIONS["destination"])

    if any(w in msg for w in ["phòng", "giá", "đặt", "còn trống", "bao nhiêu", "đơn", "đôi", "suite"]):
        return random.choice(SUGGESTIONS["room"])

    if any(w in msg for w in ["chi nhánh", "địa chỉ", "cơ sở", "ở đâu", "vị trí"]):
        return random.choice(SUGGESTIONS["branch"])

    if any(w in msg for w in ["hỗ trợ", "liên hệ", "phản hồi", "chăm sóc", "hotline"]):
        return random.choice(SUGGESTIONS["support"])

    # If not match rule, try Groq AI but avoid recursion
    try:
        return _safe_groq_reply(message)
    except Exception as e:
        logger.error(f"All reply methods failed: {e}")
        return fallback_reply()

def _safe_groq_reply(user_message: str) -> str:
    """Safe Groq API call without recursion"""
    api_key = os.getenv("apikey")
    
    if not api_key:
        logger.warning("API key not found in environment")
        return fallback_reply()
    
    try:
        logger.info(f"Attempting Groq API for: {user_message[:50]}")
        
        # FIX 1: Đơn giản hóa - không dùng requests session phức tạp
        from groq import Groq
        
        # FIX 2: Try-catch đơn giản để xử lý proxies error
        try:
            # Thử cách đơn giản nhất trước
            client = Groq(api_key=api_key)
            logger.info("Groq client created successfully (simple method)")
        except TypeError as e:
            if 'proxies' in str(e):
                logger.warning("Proxies error detected, trying workaround...")
                # CÁCH FIX PROXIES: Dùng environment variable override
                import os
                # Lưu lại environment cũ
                old_env = dict(os.environ)
                
                # Xóa tất cả proxy related environment variables
                proxy_keys = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']
                for key in proxy_keys:
                    if key in os.environ:
                        logger.info(f"Removing {key} from environment")
                        del os.environ[key]
                
                # Thử lại sau khi xóa proxy env
                client = Groq(api_key=api_key)
                logger.info("Groq client created after removing proxy env")
                
                # Khôi phục environment
                os.environ.clear()
                os.environ.update(old_env)
            else:
                raise e
        
        # FIX 3: Thử models đơn giản hơn
        system_prompt = """Bạn là trợ lý ảo của hệ thống khách sạn MelMaybe.
        Trả lời ngắn gọn, thân thiện, tập trung vào dịch vụ khách sạn.
        Luôn trả lời bằng tiếng Việt.
        
        Ví dụ về khách sạn ở Hà Nội: Khách sạn Melia, Sofitel Legend Metropole, InterContinental, Hilton."""
        
        try:
            # Thử model phổ biến nhất trước
            logger.info("Trying model: mixtral-8x7b-32768")
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=150,
                timeout=10  # Thêm timeout
            )
            
            reply = response.choices[0].message.content
            logger.info(f"Groq API success: {reply[:80]}...")
            return reply
            
        except Exception as model_error:
            logger.warning(f"Model mixtral failed: {model_error}, trying llama...")
            # Thử model khác
            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    model="llama3-70b-8192",
                    temperature=0.7,
                    max_tokens=150,
                    timeout=10
                )
                reply = response.choices[0].message.content
                logger.info(f"Groq API success with llama: {reply[:80]}...")
                return reply
            except Exception:
                # Fallback: tự tạo reply đơn giản
                if "hà nội" in user_message.lower() or "hanoi" in user_message.lower():
                    return "Hà Nội có nhiều khách sạn tuyệt vời như: Melia Hanoi, Sofitel Legend Metropole, InterContinental Hanoi, Hilton Hanoi Opera. Bạn muốn đặt phòng khách sạn nào ạ?"
                return fallback_reply()
        
    except ImportError as e:
        logger.error(f"Groq import error: {e}")
        return "⚠️ Hệ thống AI đang được cập nhật. Bạn có thể hỏi về đặt phòng, giá cả, dịch vụ khách sạn."
        
    except Exception as e:
        logger.error(f"Groq API error: {type(e).__name__}: {str(e)[:100]}")
        # FIX: Trả về reply có ý nghĩa hơn
        if "hà nội" in user_message.lower():
            return "Tại Hà Nội, hệ thống khách sạn MelMaybe có chi nhánh tại quận Hoàn Kiếm và Ba Đình với đầy đủ tiện nghi. Bạn muốn đặt phòng loại nào ạ?"
        return "Hiện tôi có thể hỗ trợ bạn đặt phòng, tư vấn điểm đến, hoặc giới thiệu dịch vụ khách sạn. Bạn cần hỗ trợ gì ạ?"

def generate_groq_reply(user_message: str) -> str:
    """Public wrapper for Groq reply"""
    return _safe_groq_reply(user_message)

def fallback_reply() -> str:
    """Simple fallback without calling other reply functions"""
    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn MelMaybe. "
        "Tôi có thể hỗ trợ bạn về: đặt phòng, thông tin chi nhánh, dịch vụ khách sạn. "
        "Bạn muốn hỏi gì ạ?"
    )
