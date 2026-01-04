from sqlalchemy import Column, Integer, Date, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date  # THÊM IMPORT NÀY!
from app.core.database import Base

class Booking(Base):
    __tablename__ = "DAT_PHONG"

    MaDatPhong = Column(Integer, primary_key=True, autoincrement=True, index=True)
    MaKH = Column(Integer, ForeignKey("KHACH_HANG.MaKH"), nullable=False)
    MaPhong = Column(Integer, ForeignKey("PHONG.MaPhong"), nullable=False)
    
    # THÊM TRƯỜNG NÀY - RẤT QUAN TRỌNG!
    NgayDat = Column(Date, default=date.today, nullable=False)  # Ngày đặt, mặc định là hôm nay
    
    NgayNhanPhong = Column(Date, nullable=False)
    NgayTraPhong = Column(Date, nullable=False)
    TongTien = Column(Numeric(10, 2), nullable=True)  # Cho phép NULL nếu chưa tính

    TrangThai = Column(
        Enum(
            "Da thanh toan",
            "Chua thanh toan", 
            "Huy",
            name="booking_trangthai_enum"
        ),
        default="Chua thanh toan",  # TRÙNG VỚI SCHEMA
        nullable=False
    )

    customer = relationship("Customer", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    reviews = relationship("Review", back_populates="booking")
