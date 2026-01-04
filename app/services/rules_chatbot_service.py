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
        
        # FIX PROXIES ISSUE: Disable proxy auto-detection
        import requests
        import urllib3
        
        # Create session without proxy
        session = requests.Session()
        session.trust_env = False  # DON'T read proxy from environment
        
        from groq import Groq
        
        # Try different ways to create client
        try:
            # Method 1: Simple client without extra params
            client = Groq(api_key=api_key)
        except TypeError as e:
            if 'proxies' in str(e):
                logger.warning("Groq client complaining about proxies, trying workaround...")
                # Method 2: Use monkey patch
                import groq._client
                
                # Save original
                original_init = groq._client.SyncClient.__init__
                
                # Create patched version
                def patched_init(self, api_key=None, **kwargs):
                    # Remove proxies from kwargs
                    kwargs.pop('proxies', None)
                    kwargs.pop('http_client', None)
                    # Call original with clean kwargs
                    return original_init(self, api_key=api_key, **kwargs)
                
                # Apply patch
                groq._client.SyncClient.__init__ = patched_init
                
                # Try again
                client = Groq(api_key=api_key)
            else:
                raise e
        
        system_prompt = """Bạn là trợ lý ảo của hệ thống khách sạn MelMaybe.
        Trả lời ngắn gọn, thân thiện, tập trung vào dịch vụ khách sạn.
        Luôn trả lời bằng tiếng Việt.
        Nếu câu hỏi không liên quan đến khách sạn, nhẹ nhàng chuyển hướng."""
        
        # Try different models
        models_to_try = ["mixtral-8x7b-32768", "llama3-70b-8192", "gemma-7b-it"]
        
        for model in models_to_try:
            try:
                logger.info(f"Trying model: {model}")
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    model=model,
                    temperature=0.7,
                    max_tokens=150
                )
                
                reply = response.choices[0].message.content
                logger.info(f"Groq API success with model {model}: {reply[:80]}...")
                return reply
                
            except Exception as model_error:
                logger.warning(f"Model {model} failed: {model_error}")
                continue
        
        # All models failed
        logger.error("All Groq models failed")
        return fallback_reply()
        
    except ImportError as e:
        logger.error(f"Groq import error: {e}")
        return "⚠️ Hệ thống AI đang được cập nhật. Bạn có thể hỏi về đặt phòng, giá cả, dịch vụ khách sạn."
        
    except Exception as e:
        logger.error(f"Groq API error: {type(e).__name__}: {str(e)[:100]}")
        # Return simple fallback, NOT generate_reply() to avoid recursion
        return "Tôi hiện không thể kết nối đến hệ thống AI. Bạn muốn hỏi gì về dịch vụ khách sạn không?"

def generate_groq_reply(user_message: str) -> str:
    """Public wrapper for Groq reply"""
    # Avoid recursion by using safe version
    return _safe_groq_reply(user_message)

def fallback_reply() -> str:
    """Simple fallback without calling other reply functions"""
    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn MelMaybe. "
        "Tôi có thể hỗ trợ bạn về: đặt phòng, thông tin chi nhánh, dịch vụ khách sạn. "
        "Bạn muốn hỏi gì ạ?"
    )

def test_groq_import():
    """Test function to check groq installation"""
    try:
        import groq
        return f"✅ Groq imported. Version: {getattr(groq, '__version__', 'unknown')}"
    except ImportError as e:
        return f"❌ Groq import failed: {e}"
