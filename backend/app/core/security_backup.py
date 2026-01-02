from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone  # ← THÊM timezone
from jose import JWTError, ExpiredSignatureError   # ← THÊM ExpiredSignatureError
from jose import jwt  # ← ĐỔI từ 'from jose import jwt' thành 'import jwt'
from fastapi import HTTPException, status
from app.core.config import config

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

# Password hasching - Giữ bcrypt (ổn định) hoặc dùng argon2 (bảo mật hơn)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_token(data: dict, typ: str = 'access'):
    to_encode = data.copy()
    
    # Dùng timezone-aware datetime
    if typ == 'access':
        expire = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:  # refresh token
        expire = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": typ})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
