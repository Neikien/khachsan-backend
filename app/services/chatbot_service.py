import random

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
    msg = message.lower()

    if any(w in msg for w in ["đi đâu", "địa điểm", "du lịch", "tham quan"]):
        return random.choice(SUGGESTIONS["destination"])

    if any(w in msg for w in ["phòng", "giá", "đặt", "còn trống"]):
        return random.choice(SUGGESTIONS["room"])

    if any(w in msg for w in ["chi nhánh", "địa chỉ", "cơ sở"]):
        return random.choice(SUGGESTIONS["branch"])

    if any(w in msg for w in ["hỗ trợ", "liên hệ", "phản hồi", "chăm sóc"]):
        return random.choice(SUGGESTIONS["support"])

    return (
        "Xin chào! Tôi là trợ lý ảo của hệ thống khách sạn. "
        "Tôi có thể hỗ trợ đặt phòng, gợi ý địa điểm hoặc cung cấp thông tin chi nhánh. "
        "Bạn muốn hỏi gì ạ?"
    )
