from pydantic import BaseModel
from typing import Optional

class HotelCreate(BaseModel):
    TenKS: str
    DiaChi: str
    SoSao: int
    MaKhuVuc: int
    MoTa: Optional[str] = None

class HotelUpdate(BaseModel):
    TenKS: Optional[str] = None
    DiaChi: Optional[str] = None
    SoSao: Optional[int] = None
    MaKhuVuc: Optional[int] = None
    MoTa: Optional[str] = None

class HotelResponse(BaseModel):
    MaKS: int
    TenKS: str
    DiaChi: str
    SoSao: int
    MaKhuVuc: int
    MoTa: Optional[str]

    class Config:
        from_attributes = True
