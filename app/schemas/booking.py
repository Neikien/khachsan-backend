from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date
from enum import Enum

class BookingStatus(str, Enum):
    # PHẢI KHỚP CHÍNH XÁC với Enum trong database!
    da_thanh_toan = 'Da thanh toan'      # ← KHÔNG DẤU, KHÔNG VIẾT HOA
    chua_thanh_toan = 'Chua thanh toan'  # ← KHÔNG DẤU, KHÔNG VIẾT HOA  
    huy = 'Huy'                          # ← KHÔNG DẤU, KHÔNG VIẾT HOA
    # KHÔNG CÓ "Đã đặt" vì database không có!

class BookingCreate(BaseModel):
    MaKH: int
    MaPhong: int
    NgayNhanPhong: date
    NgayTraPhong: date
    NgayDat: date = Field(default_factory=date.today)
    # SỬA LẠI CHO ĐÚNG VỚI DATABASE!
    TrangThai: BookingStatus = Field(default=BookingStatus.chua_thanh_toan)  # ← DÙNG ENUM
    TongTien: Optional[Decimal] = None

class BookingUpdate(BaseModel):
    NgayNhanPhong: Optional[date] = None
    NgayTraPhong: Optional[date] = None
    TongTien: Optional[Decimal] = None
    TrangThai: Optional[BookingStatus] = None

class BookingResponse(BaseModel):
    MaDatPhong: int
    MaKH: int
    MaPhong: int
    NgayDat: date
    NgayNhanPhong: date
    NgayTraPhong: date
    TongTien: Optional[Decimal]
    TrangThai: BookingStatus

    class Config:
        from_attributes = True
