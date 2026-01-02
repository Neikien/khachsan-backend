from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum

class ReviewStatus(str, Enum):
    hien_thi = 'Hiển thị'
    an = 'Ẩn'

class ReviewCreate(BaseModel):
    MaDatPhong: int
    Diem: int
    NoiDung: str

class ReviewUpdate(BaseModel):
    Diem: Optional[int] = None
    NoiDung: Optional[str] = None
    TrangThai: Optional[ReviewStatus] = None

class ReviewResponse(BaseModel):
    MaDanhGia: int
    MaDatPhong: int
    Diem: int
    NoiDung: str
    NgayDanhGia: date
    TrangThai: ReviewStatus

    class Config:
        from_attributes = True
