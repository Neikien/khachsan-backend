from pydantic import BaseModel, ConfigDict, field_serializer
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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v) if v is not None else None
        }
    )
    
    @field_serializer('GiaDV')
    def serialize_gia_dv(self, gia_dv: Decimal, _info):
        """Convert Decimal to float for JSON response"""
        return float(gia_dv) if gia_dv else None
