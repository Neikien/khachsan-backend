from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from app.core.database import Base

class Booking(Base):
    __tablename__ = "DAT_PHONG"

    MaDatPhong = Column(Integer, primary_key=True, autoincrement=True, index=True)
    MaKH = Column(Integer, ForeignKey("KHACH_HANG.MaKH"), nullable=False)
    MaPhong = Column(Integer, ForeignKey("PHONG.MaPhong"), nullable=False)
    
    NgayDat = Column('ngaydat', Date, default=date.today, nullable=False)
    NgayNhanPhong = Column(Date, nullable=False)
    NgayTraPhong = Column(Date, nullable=False)
    TongTien = Column(Numeric(10, 2), nullable=True)
    
    # THAY ENUM BẰNG VARCHAR
    TrangThai = Column(
        'TrangThai',  # Tên cột
        nullable=False,
        default='Chua thanh toan'  # Giá trị mặc định
    )

    customer = relationship("Customer", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    reviews = relationship("Review", back_populates="booking")

