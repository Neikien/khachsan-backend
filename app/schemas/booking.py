from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date
from enum import Enum

class BookingStatus(str, Enum):
    da_thanh_toan = 'Đã thanh toán'
    chua_thanh_toan = 'Chưa thanh toán'
    huy = 'Hủy'
    da_dat = 'Đã đặt'  # THÊM TRẠNG THÁI NÀY!

class BookingCreate(BaseModel):
    MaKH: int
    MaPhong: int
    NgayNhanPhong: date
    NgayTraPhong: date
    # THÊM 2 TRƯỜNG NÀY VỚI GIÁ TRỊ DEFAULT
    NgayDat: date = Field(default_factory=date.today)
    TrangThai: str = Field(default="Đã đặt")
    # Thêm TongTien nếu cần
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
    NgayDat: date  # THÊM VÀO RESPONSE
    NgayNhanPhong: date
    NgayTraPhong: date
    TongTien: Optional[Decimal]
    TrangThai: BookingStatus

    class Config:
        from_attributes = True
