from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class CustomerCreate(BaseModel):
    HoTen: str
    SoDienThoai: Optional[str] = None
    Email: Optional[EmailStr] = None
    CCCD: Optional[str] = None
    DiaChi: Optional[str] = None

class CustomerUpdate(BaseModel):
    HoTen: Optional[str] = None
    SoDienThoai: Optional[str] = None
    Email: Optional[EmailStr] = None
    CCCD: Optional[str] = None
    DiaChi: Optional[str] = None

class CustomerResponse(BaseModel):
    MaKH: int
    HoTen: str
    SoDienThoai: Optional[str]
    Email: Optional[str]
    CCCD: Optional[str]
    DiaChi: Optional[str]

    class Config:
        from_attributes = True
