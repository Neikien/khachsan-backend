import os
import logging
from typing import Dict, List, Optional
from sqlalchemy import text
from app.core.database import engine

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.api_key = os.getenv("apikey") or os.getenv("GROQ_API_KEY")
        self.base_url = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    async def _query_database(self, query: str, params: Dict = None) -> List[Dict]:
        try:
            async with engine.connect() as conn:
                result = await conn.execute(text(query), params or {})
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return []
    
    async def get_hotel_info(self) -> List[Dict]:
        try:
            hotels = await self._query_database("""
                SELECT 
                    MaKS as id,
                    TenKS as name, 
                    DiaChi as location,
                    SoSao as star_rating,
                    MoTa as description
                FROM KHACH_SAN 
                ORDER BY MaKS
                LIMIT 10
            """)
            return hotels
        except Exception as e:
            logger.error(f"Error getting hotel info: {e}")
            return []
    
    async def get_room_info(self, hotel_id: Optional[int] = None) -> List[Dict]:
        try:
            if hotel_id:
                rooms = await self._query_database("""
                    SELECT 
                        p.MaPhong as id,
                        p.MaKS as hotel_id,
                        p.LoaiPhong as room_type,
                        p.GiaPhong as price,
                        p.TinhTrang as status,
                        k.TenKS as hotel_name,
                        k.DiaChi as hotel_location
                    FROM PHONG p
                    LEFT JOIN KHACH_SAN k ON p.MaKS = k.MaKS
                    WHERE p.MaKS = :hotel_id
                    ORDER BY p.GiaPhong
                    LIMIT 15
                """, {"hotel_id": hotel_id})
            else:
                rooms = await self._query_database("""
                    SELECT 
                        p.MaPhong as id,
                        p.MaKS as hotel_id,
                        p.LoaiPhong as room_type,
                        p.GiaPhong as price,
                        p.TinhTrang as status,
                        k.TenKS as hotel_name,
                        k.DiaChi as hotel_location
                    FROM PHONG p
                    LEFT JOIN KHACH_SAN k ON p.MaKS = k.MaKS
                    WHERE p.TinhTrang = 'Trống'
                    ORDER BY p.MaKS, p.GiaPhong
                    LIMIT 20
                """)
            return rooms
        except Exception as e:
            logger.error(f"Error getting room info: {e}")
            return []
    
    async def get_booking_stats(self) -> Dict:
        try:
            stats = await self._query_database("""
                SELECT 
                    COUNT(*) as total_bookings,
                    COUNT(CASE WHEN DATE(NgayDat) = CURRENT_DATE THEN 1 END) as today_bookings,
                    COUNT(CASE WHEN TrangThai = 'Đã xác nhận' THEN 1 END) as confirmed_bookings
                FROM DAT_PHONG
            """)
            return stats[0] if stats else {"total_bookings": 0, "today_bookings": 0, "confirmed_bookings": 0}
        except Exception as e:
            logger.error(f"Error getting booking stats: {e}")
            return {"total_bookings": 0, "today_bookings": 0, "confirmed_bookings": 0}
    
    def _format_data_for_prompt(self, hotels: List[Dict], rooms: List[Dict], stats: Dict) -> str:
        prompt_parts = []
        
        prompt_parts.append(f"📊 THỐNG KÊ HỆ THỐNG:")
        prompt_parts.append(f"- Tổng số booking: {stats.get('total_bookings', 0)}")
        prompt_parts.append(f"- Booking hôm nay: {stats.get('today_bookings', 0)}")
        prompt_parts.append(f"- Booking đã xác nhận: {stats.get('confirmed_bookings', 0)}")
        
        if hotels:
            prompt_parts.append(f"\n🏨 DANH SÁCH KHÁCH SẠN ({len(hotels)} khách sạn 5 sao):")
            for hotel in hotels[:5]:
                name = hotel.get('name', 'Khách sạn')
                location = hotel.get('location', '')
                stars = hotel.get('star_rating', 5)
                prompt_parts.append(f"- {name}: {location[:50]}... ({stars} sao)")
        else:
            prompt_parts.append("\n🏨 Chưa có thông tin khách sạn.")
        
        available_rooms = [r for r in rooms if r.get('status') == 'Trống']
        if available_rooms:
            prompt_parts.append(f"\n🛏️ PHÒNG TRỐNG HIỆN CÓ ({len(available_rooms)} phòng):")
            
            rooms_by_hotel = {}
            for room in available_rooms[:10]:
                hotel_name = room.get('hotel_name', 'Khách sạn')
                if hotel_name not in rooms_by_hotel:
                    rooms_by_hotel[hotel_name] = []
                rooms_by_hotel[hotel_name].append(room)
            
            for hotel_name, hotel_rooms in rooms_by_hotel.items():
                prompt_parts.append(f"\n{hotel_name}:")
                for room in hotel_rooms[:3]:
                    room_type = room.get('room_type', '')
                    price = room.get('price', 0)
                    formatted_price = f"{price:,.0f} VND" if price else "Liên hệ"
                    prompt_parts.append(f"  - {room_type}: {formatted_price}/đêm")
        else:
            prompt_parts.append("\n🛏️ Không có phòng trống.")
        
        return "\n".join(prompt_parts)
    
    async def generate_context(self, user_message: str) -> str:
        hotels = await self.get_hotel_info()
        rooms = await self.get_room_info()
        stats = await self.get_booking_stats()
        
        db_context = self._format_data_for_prompt(hotels, rooms, stats)
        
        full_context = f"""
        {db_context}
        
        ---
        
        CÂU HỎI CỦA KHÁCH: {user_message}
        
        HƯỚNG DẪN CHO AI:
        - Trả lời dựa trên thông tin thực tế từ database ở trên
        - Nếu không có thông tin, thành thật nói "Hiện chưa có thông tin về..."
        - Luôn trả lời bằng tiếng Việt, thân thiện, chuyên nghiệp
        - Với câu hỏi về giá/phòng, tham khảo giá từ danh sách phòng trống
        - Với câu hỏi về địa điểm, tham khảo địa chỉ khách sạn trong danh sách
        - Giữ câu trả lời ngắn gọn, tập trung vào thông tin khách cần
        """
        
        return full_context
    
    def sync_generate_reply(self, user_message: str) -> str:
        try:
            import asyncio
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: loop.run_until_complete(self.generate_reply(user_message)))
                    return future.result()
            else:
                return loop.run_until_complete(self.generate_reply(user_message))
                
        except Exception as e:
            logger.error(f"Error in sync_generate_reply: {e}")
            return self._fallback_reply(user_message)
    
    async def generate_reply(self, user_message: str) -> str:
        try:
            if not self.api_key:
                return self._fallback_reply(user_message)
            
            context = await self.generate_context(user_message)
            
            try:
                from openai import OpenAI
                
                client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "Bạn là trợ lý ảo của hệ thống khách sạn MelMaybe. Bạn có quyền truy cập vào database thực tế. LUÔN trả lời dựa trên thông tin thực tế được cung cấp từ database. Nếu không có thông tin trong database, thành thật nói 'Hiện chưa có thông tin về vấn đề này'. Luôn trả lời bằng tiếng Việt."
                        },
                        {
                            "role": "user", 
                            "content": context
                        }
                    ],
                    temperature=0.7,
                    max_tokens=200,
                    timeout=30.0
                )
                
                return response.choices[0].message.content
                
            except ImportError:
                from groq import Groq
                
                client = Groq(api_key=self.api_key)
                
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Bạn là trợ lý khách sạn với dữ liệu thực tế."},
                        {"role": "user", "content": context}
                    ],
                    model="mixtral-8x7b-32768",
                    temperature=0.7,
                    max_tokens=200
                )
                
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Chatbot service error: {e}")
            return self._fallback_reply(user_message)
    
    def _fallback_reply(self, user_message: str) -> str:
        msg = user_message.lower()
        
        if any(w in msg for w in ["phòng", "giá", "đặt phòng"]):
            return "Hiện có phòng Đơn từ 1.5-2 triệu, phòng Đôi 2.5-3 triệu, phòng VIP 5 triệu."
        
        if any(w in msg for w in ["khách sạn", "địa chỉ", "chi nhánh"]):
            return "MelMaybe có 5 chi nhánh 5 sao tại: Hà Nội, Đà Nẵng, Nha Trang, Đà Lạt, TP.HCM."
        
        if "cảm ơn" in msg:
            return "Cảm ơn bạn! Chúc bạn một ngày tốt lành!"
        
        return "Xin chào! Tôi có thể giúp bạn tìm thông tin khách sạn, phòng trống và đặt phòng."

chatbot_service = ChatbotService()
