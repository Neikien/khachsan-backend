from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date

class BookingCreate(BaseModel):
    MaKH: int
    MaPhong: int
    NgayNhanPhong: date
    NgayTraPhong: date
    NgayDat: date = Field(default_factory=date.today)
    TrangThai: str = Field(default="Chua thanh toan")  # STRING THƯỜNG
    TongTien: Optional[Decimal] = None

class BookingUpdate(BaseModel):
    NgayNhanPhong: Optional[date] = None
    NgayTraPhong: Optional[date] = None
    TongTien: Optional[Decimal] = None
    TrangThai: Optional[str] = None  # STRING THƯỜNG

class BookingResponse(BaseModel):
    MaDatPhong: int
    MaKH: int
    MaPhong: int
    NgayDat: date
    NgayNhanPhong: date
    NgayTraPhong: date
    TongTien: Optional[Decimal]
    TrangThai: str  # STRING THƯỜNG

    class Config:
        from_attributes = True
