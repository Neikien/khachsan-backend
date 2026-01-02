from pydantic import BaseModel
from typing import Optional

class AreaCreate(BaseModel):
    TenKhuVuc: str
    MoTa: Optional[str] = None
    ViTri: Optional[str] = None

class AreaUpdate(BaseModel):
    TenKhuVuc: Optional[str] = None
    MoTa: Optional[str] = None
    ViTri: Optional[str] = None

class AreaResponse(BaseModel):
    MaKhuVuc: int
    TenKhuVuc: str
    MoTa: Optional[str]
    ViTri: Optional[str]

    class Config:
        from_attributes = True
