from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = 'admin'
    khach_hang = 'khach_hang'
    nhan_vien = 'nhan_vien'

class UserStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    fullname: str
    role: UserRole = UserRole.khach_hang

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    fullname: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    fullname: str
    role: UserRole
    status: UserStatus
    created_at: datetime  

    class Config:
        from_attributes = True