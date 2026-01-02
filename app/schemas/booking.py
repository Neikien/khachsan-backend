from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date
from enum import Enum

class BookingStatus(str, Enum):
    da_thanh_toan = 'Đã thanh toán'
    chua_thanh_toan = 'Chưa thanh toán'
    huy = 'Hủy'

class BookingCreate(BaseModel):
    MaKH: int
    MaPhong: int
    NgayNhanPhong: date
    NgayTraPhong: date

class BookingUpdate(BaseModel):
    NgayNhanPhong: Optional[date] = None
    NgayTraPhong: Optional[date] = None
    TongTien: Optional[Decimal] = None
    TrangThai: Optional[BookingStatus] = None

class BookingResponse(BaseModel):
    MaDatPhong: int
    MaKH: int
    MaPhong: int
    NgayNhanPhong: date
    NgayTraPhong: date
    TongTien: Optional[Decimal]
    TrangThai: BookingStatus

    class Config:
        from_attributes = True
