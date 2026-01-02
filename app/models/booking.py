from sqlalchemy import Column, Integer, Date, Numeric, Enum, ForeignKey 
from sqlalchemy.orm import relationship 
from app.core.database import Base 
 
class Booking(Base): 
    __tablename__ = "DAT_PHONG" 
 
    MaDatPhong = Column(Integer, primary_key=True, autoincrement=True, index=True) 
    MaKH = Column(Integer, ForeignKey("KHACH_HANG.MaKH")) 
    MaPhong = Column(Integer, ForeignKey("PHONG.MaPhong")) 
    NgayNhanPhong = Column(Date, nullable=False) 
    NgayTraPhong = Column(Date, nullable=False) 
    TongTien = Column(Numeric(10, 2)) 
    TrangThai = Column(Enum('Da thanh toan', 'Chua thanh toan', 'Huy'), default='Chua thanh toan') 
 
    # Relationships - SUA 
    customer = relationship("Customer")  # BO back_populates 
    room = relationship("Room")  # BO back_populates 
    # service_usages = relationship("ServiceUsage", back_populates="booking")  # TAM COMMENT 
    reviews = relationship("Review")  # BO back_populates 
