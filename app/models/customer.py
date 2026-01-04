from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Customer(Base):
    __tablename__ = "KHACH_HANG"

    MaKH = Column(Integer, primary_key=True, autoincrement=True, index=True)
    HoTen = Column(String(100), nullable=False)
    SoDienThoai = Column(String(15))
    Email = Column(String(100))
    CCCD = Column(String(20))
    DiaChi = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Relationships
    user = relationship("User", back_populates="customer")
    
    # THÊM DÒNG NÀY - QUAN TRỌNG
    bookings = relationship("Booking", back_populates="customer")  # ← THÊM
