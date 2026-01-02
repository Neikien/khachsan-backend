from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Numeric 
from sqlalchemy.orm import relationship 
from app.core.database import Base 
 
class Room(Base): 
    __tablename__ = "PHONG" 
 
    MaPhong = Column(Integer, primary_key=True, autoincrement=True, index=True) 
    MaKS = Column(Integer, ForeignKey("KHACH_SAN.MaKS")) 
    LoaiPhong = Column(String(50), nullable=False) 
    GiaPhong = Column(Numeric(10, 2), nullable=False) 
    TinhTrang = Column(Enum('Trống', 'Đã đặt', 'Bảo trì'), default='Trống')
 
    hotel = relationship("Hotel")  
    bookings = relationship("Booking") 


