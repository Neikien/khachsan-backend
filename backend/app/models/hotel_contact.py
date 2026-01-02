from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class HotelContact(Base):
    __tablename__ = "LIEN_HE_KHACH_SAN"
    
    MaLienHe = Column(Integer, primary_key=True, autoincrement=True, index=True)
    MaKS = Column(Integer, ForeignKey("KHACH_SAN.MaKS"))
    HoTenNguoiLienHe = Column(String(100))
    ChucVu = Column(String(50))
    SoDienThoai = Column(String(15))
    Email = Column(String(100))
    GhiChu = Column(Text)
    
    # Relationships
    hotel = relationship("Hotel")
