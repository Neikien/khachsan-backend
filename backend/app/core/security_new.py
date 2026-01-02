from fastapi.security import OAuth2PasswordBearer 
from passlib.context import CryptContext 
from datetime import datetime, timedelta, timezone 
from jose import JWTError, ExpiredSignatureError 
from jose import jwt 
from fastapi import HTTPException, status 
from app.core.config import config 
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login') 
 
"# Sửa bcrypt thành argon2 (trách lỗi)" 
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto") 
 
def verify_password(plain_password: str, hashed_password: str) -
    return pwd_context.verify(plain_password, hashed_password) 
 
def hash_password(password: str) -
    return pwd_context.hash(password) 
 
def create_token(data: dict, typ: str = 'access'): 
    to_encode = data.copy() 
 
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
