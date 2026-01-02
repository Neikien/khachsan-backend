from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class Role(str, Enum):
    admin = 'admin'
    khach_hang = 'khach_hang'
    nhan_vien = 'nhan_vien'

class SignupRequest(BaseModel):
    username: str
    password: str
    email: EmailStr
    fullname: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    fullname: str
    role: Role
    # XÓA: customer_id: Optional[int] = None
    # THÊM: user_id cho KHACH_HANG
    user_id: Optional[int] = None  # Nếu cần

class UserUpdate(BaseModel):
    current_password: str
    new_password: Optional[str] = None
    email: Optional[EmailStr] = None
    fullname: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str