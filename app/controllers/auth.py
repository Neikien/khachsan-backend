from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
from botocore.client import BaseClient
import re
from email_validator import validate_email, EmailNotValidError
from app.schemas.auth import SignupRequest, UserResponse, UserUpdate
from app.core.config import config
from app.core.dependencies import get_db, get_current_user, get_s3_client
from app.core.security import verify_password, hash_password, create_token, verify_token
from app.models.user import User
from app.models.customer import Customer
from datetime import datetime, timedelta, timezone
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post('/login')
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(
            or_(
                User.username == form_data.username,
                User.email == form_data.username
            )
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=400, detail="Invalid username/email or password")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username/email or password")

    access_token = create_token({'sub': user.id})
    refresh_token = create_token({'sub': user.id}, typ='refresh')

    response.set_cookie(
        key="rt",
        value=refresh_token,
        httponly=True,
        secure=True,
        expires=datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/signup')
async def signup(form_data: SignupRequest, db: AsyncSession = Depends(get_db)):
    logger.info(f"Signup attempt: {form_data.username}, {form_data.email}")
    
    errors = {}
    
    try:
        validate_email(form_data.email)
    except EmailNotValidError:
        errors['email'] = "Email không hợp lệ"
    
    password = form_data.password
    if len(password) < 6:
        errors['password_length'] = "Mật khẩu phải có ít nhất 6 ký tự"
    if not re.search(r'[A-Z]', password):
        errors['password_upper'] = "Mật khẩu phải có ít nhất 1 chữ hoa"
    if not re.search(r'[a-z]', password):
        errors['password_lower'] = "Mật khẩu phải có ít nhất 1 chữ thường"
    if not re.search(r'[0-9]', password):
        errors['password_digit'] = "Mật khẩu phải có ít nhất 1 số"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors['password_special'] = "Mật khẩu phải có ít nhất 1 ký tự đặc biệt"
    
    if form_data.fullname:
        stripped = form_data.fullname.strip()
        if stripped != form_data.fullname:
            errors['fullname'] = "Tên không được có khoảng trắng ở đầu hoặc cuối"
        if len(stripped.split()) < 2:
            errors['fullname_format'] = "Vui lòng nhập đầy đủ họ và tên"
    
    if ' ' in form_data.username:
        errors['username'] = "Username không được chứa khoảng trắng"
    
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    existing = result.scalar_one_or_none()

    if existing:
        logger.warning(f"Username already exists: {form_data.username}")
        raise HTTPException(status_code=400, detail="Username already exists")

    result_email = await db.execute(
        select(User).where(User.email == form_data.email)
    )
    existing_email = result_email.scalar_one_or_none()

    if existing_email:
        logger.warning(f"Email already exists: {form_data.email}")
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pwd = hash_password(form_data.password)

    user = User(
        username=form_data.username,
        password=hashed_pwd,
        email=form_data.email,
        fullname=form_data.fullname,
        role="user",
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"✅ Created user ID: {user.id}, username: {user.username}")

    try:
        customer = Customer(
            HoTen=form_data.fullname,
            Email=form_data.email,
            SoDienThoai="",
            CCCD="",
            DiaChi="",
            user_id=user.id
        )
        
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        logger.info(f"✅ Created customer ID: {customer.MaKH}, linked to user {user.id}")
        
        return {
            'message': 'User created successfully',
            'user_id': user.id,
            'customer_id': customer.MaKH
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating customer for user {user.id}: {e}", exc_info=True)
        return {
            'message': 'User created successfully but customer profile creation failed',
            'user_id': user.id,
        }

@router.get('/info', response_model=UserResponse)
async def get_user(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie('rt')
    return {'message': 'Logout successfully'}

@router.post('/refresh')
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    old_rt = request.cookies.get('rt')

    payload = verify_token(old_rt)
    user_id = payload.get('sub')

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists")

    new_rt = create_token({'sub': user_id}, typ='refresh')
    response.set_cookie(
        key="rt",
        value=new_rt,
        httponly=True,
        secure=True,
        expires=datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    new_at = create_token({'sub': user_id})
    return {"access_token": new_at, "token_type": "bearer"}

@router.patch('/update')
async def update_user(
    request: UserUpdate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    cur_user = result.scalar_one_or_none()

    if not cur_user:
        raise HTTPException(status_code=404, detail="User not found")

    errors = {}

    if not verify_password(request.current_password, cur_user.password):
        errors['password'] = "Current password is incorrect"

    if request.email and request.email != cur_user.email:
        try:
            validate_email(request.email)
        except EmailNotValidError:
            errors['email'] = "Email không hợp lệ"
        
        email_result = await db.execute(select(User).where(User.email == request.email))
        existing_email = email_result.scalar_one_or_none()
        if existing_email:
            errors['email_exists'] = "Email already exists"

    if request.new_password:
        password = request.new_password
        if len(password) < 6:
            errors['new_password_length'] = "Mật khẩu phải có ít nhất 6 ký tự"
        if not re.search(r'[A-Z]', password):
            errors['new_password_upper'] = "Mật khẩu phải có ít nhất 1 chữ hoa"
        if not re.search(r'[a-z]', password):
            errors['new_password_lower'] = "Mật khẩu phải có ít nhất 1 chữ thường"
        if not re.search(r'[0-9]', password):
            errors['new_password_digit'] = "Mật khẩu phải có ít nhất 1 số"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors['new_password_special'] = "Mật khẩu phải có ít nhất 1 ký tự đặc biệt"

    if request.fullname:
        stripped = request.fullname.strip()
        if stripped != request.fullname:
            errors['fullname'] = "Tên không được có khoảng trắng ở đầu hoặc cuối"

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    update_data = {}
    if request.email:
        update_data['email'] = request.email
    if request.fullname:
        update_data['fullname'] = request.fullname
    if request.new_password:
        update_data['password'] = hash_password(request.new_password)

    if update_data:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await db.commit()

    return {"message": "User updated successfully"}

@router.delete('/delete')
async def delete_account(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    s3_client: BaseClient = Depends(get_s3_client)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(User.__table__.delete().where(User.id == user_id))
    await db.commit()

    return {"message": "Account and related data deleted successfully"}
