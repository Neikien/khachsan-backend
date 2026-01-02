from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActivityLogCreate(BaseModel):
    user_id: int
    HanhDong: str
    MoTa: Optional[str] = None

class ActivityLogResponse(BaseModel):
    MaHoatDong: int
    user_id: int
    HanhDong: str
    MoTa: Optional[str]
    ThoiGian: datetime

    class Config:
        from_attributes = True
