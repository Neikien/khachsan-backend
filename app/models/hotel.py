from sqlalchemy import Column, Integer, String, Text, ForeignKey 
from sqlalchemy.orm import relationship 
from app.core.database import Base 
 
class Hotel(Base): 
    __tablename__ = "KHACH_SAN" 
 
    MaKS = Column(Integer, primary_key=True, autoincrement=True, index=True) 
    TenKS = Column(String(100), nullable=False) 
    DiaChi = Column(String(255), nullable=False) 
    SoSao = Column(Integer) 
    MaKhuVuc = Column(Integer, ForeignKey("KHU_VUC.MaKhuVuc")) 
    MoTa = Column(Text) 
 
    area = relationship("Area")  
    rooms = relationship("Room")  

