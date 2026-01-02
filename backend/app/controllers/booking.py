from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import date
from app.core.dependencies import get_db, get_current_user
from app.schemas.booking import BookingResponse, BookingCreate, BookingUpdate
from app.models.booking import Booking
from app.models.room import Room
from app.models.customer import Customer

router = APIRouter()

@router.get("/", response_model=List[BookingResponse])
async def get_bookings(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Booking).offset(skip).limit(limit)
    )
    bookings = result.scalars().all()
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Booking).where(Booking.MaDatPhong == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if customer exists
    customer_result = await db.execute(
        select(Customer).where(Customer.MaKH == booking_data.MaKH)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found")
    
    # Check if room exists and is available
    room_result = await db.execute(
        select(Room).where(Room.MaPhong == booking_data.MaPhong)
    )
    room = room_result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(status_code=400, detail="Room not found")
    
    if room.TinhTrang != 'Trống':
        raise HTTPException(status_code=400, detail="Room is not available")
    
    # Check for booking conflicts
    conflict_result = await db.execute(
        select(Booking).where(
            and_(
                Booking.MaPhong == booking_data.MaPhong,
                Booking.NgayNhanPhong < booking_data.NgayTraPhong,
                Booking.NgayTraPhong > booking_data.NgayNhanPhong,
                Booking.TrangThai != 'Hủy'
            )
        )
    )
    conflicting_booking = conflict_result.scalar_one_or_none()
    
    if conflicting_booking:
        raise HTTPException(status_code=400, detail="Room is already booked for these dates")
    
    booking = Booking(**booking_data.model_dump())
    db.add(booking)
    
    # Update room status
    room.TinhTrang = 'Đã đặt'
    
    await db.commit()
    await db.refresh(booking)
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Booking).where(Booking.MaDatPhong == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    for field, value in booking_data.model_dump(exclude_unset=True).items():
        setattr(booking, field, value)
    
    await db.commit()
    await db.refresh(booking)
    return booking

@router.delete("/{booking_id}")
async def cancel_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Booking).where(Booking.MaDatPhong == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update room status back to available
    room_result = await db.execute(
        select(Room).where(Room.MaPhong == booking.MaPhong)
    )
    room = room_result.scalar_one_or_none()
    
    if room:
        room.TinhTrang = 'Trống'
    
    booking.TrangThai = 'Hủy'
    await db.commit()
    return {"message": "Booking cancelled successfully"}
