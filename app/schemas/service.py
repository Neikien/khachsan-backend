from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ServiceCreate(BaseModel):
    TenDV: str
    GiaDV: Decimal
    MoTa: Optional[str] = None

class ServiceUpdate(BaseModel):
    TenDV: Optional[str] = None
    GiaDV: Optional[Decimal] = None
    MoTa: Optional[str] = None

class ServiceResponse(BaseModel):
    MaDV: int
    TenDV: str
    GiaDV: Decimal
    MoTa: Optional[str]

    class Config:
        from_attributes = True
