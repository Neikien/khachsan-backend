from sqlalchemy import Column, Integer, Text, Date, String, ForeignKey 
from sqlalchemy.orm import relationship 
from app.core.database import Base 
 
class Review(Base): 
    __tablename__ = "DANH_GIA" 
 
    MaDanhGia = Column(Integer, primary_key=True, autoincrement=True, index=True) 
    MaDatPhong = Column(Integer, ForeignKey("DAT_PHONG.MaDatPhong")) 
    Diem = Column(Integer) 
    NoiDung = Column(Text) 
    NgayDanhGia = Column(Date) 
    TrangThai = Column(String(20), default='Hien thi')  # ← ĐÃ SỬA
 
    booking = relationship("Booking")
