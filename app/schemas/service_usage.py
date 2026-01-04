# schemas/service_usage.py
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import date
from typing import Optional

class ServiceUsageCreate(BaseModel):
    MaDatPhong: int = Field(..., description="Mã đặt phòng")
    MaDV: int = Field(..., description="Mã dịch vụ")
    SoLuong: int = Field(default=1, gt=0, description="Số lượng sử dụng")
    ThanhTien: Optional[Decimal] = Field(
        None, 
        description="Thành tiền (tự động tính nếu không nhập)"
    )

class ServiceUsageUpdate(BaseModel):
    SoLuong: Optional[int] = Field(None, gt=0, description="Số lượng sử dụng")
    ThanhTien: Optional[Decimal] = Field(None, description="Thành tiền")

class ServiceUsageResponse(BaseModel):
    MaSuDung: int = Field(..., description="Mã sử dụng dịch vụ")
    MaDatPhong: int = Field(..., description="Mã đặt phòng")
    MaDV: int = Field(..., description="Mã dịch vụ")
    SoLuong: int = Field(..., description="Số lượng sử dụng")
    ThanhTien: Optional[Decimal] = Field(None, description="Thành tiền")
    
    # Pydantic v2 style
    model_config = ConfigDict(from_attributes=True)
