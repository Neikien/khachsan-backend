from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import config
from app.core.security import oauth2_scheme, verify_token
from app.models.user import User
from sqlalchemy import select

async def get_db():
    async with config.AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(access_token: str = Depends(oauth2_scheme)):
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return payload.get('sub')

async def get_current_active_user(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Tìm user trong SQL để verify user còn tồn tại
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

def get_s3_client():
    return config.S3_CLIENT
