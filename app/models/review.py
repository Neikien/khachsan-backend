from sqlalchemy import Column, Integer, Text, Date, Enum, ForeignKey 
from sqlalchemy.orm import relationship 
from app.core.database import Base 
 
class Review(Base): 
    __tablename__ = "DANH_GIA" 
 
    MaDanhGia = Column(Integer, primary_key=True, autoincrement=True, index=True) 
    MaDatPhong = Column(Integer, ForeignKey("DAT_PHONG.MaDatPhong")) 
    Diem = Column(Integer) 
    NoiDung = Column(Text) 
    NgayDanhGia = Column(Date) 
    TrangThai = Column(Enum('Hien thi', 'An'), default='Hien thi') 
 
    # Relationships - SUA 
    booking = relationship("Booking")  # BO back_populates 
