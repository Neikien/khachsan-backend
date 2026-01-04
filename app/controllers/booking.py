from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import date
import logging
from app.core.dependencies import get_db, get_current_user
from app.schemas.booking import BookingResponse, BookingCreate, BookingUpdate
from app.models.booking import Booking
from app.models.room import Room
from app.models.customer import Customer

# Setup logging
logger = logging.getLogger(__name__)

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
    logger.info(f"📥 Received booking request: {booking_data.model_dump()}")
    
    try:
        # 1. VALIDATE DATES
        if booking_data.NgayTraPhong <= booking_data.NgayNhanPhong:
            logger.warning(f"❌ Invalid dates: check-out {booking_data.NgayTraPhong} <= check-in {booking_data.NgayNhanPhong}")
            raise HTTPException(
                status_code=400, 
                detail="Ngày trả phòng phải sau ngày nhận phòng"
            )
        
        # 2. CHECK CUSTOMER EXISTS
        logger.info(f"🔍 Checking customer with MaKH={booking_data.MaKH}")
        customer_result = await db.execute(
            select(Customer).where(Customer.MaKH == booking_data.MaKH)
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer:
            logger.warning(f"❌ Customer not found: MaKH={booking_data.MaKH}")
            raise HTTPException(status_code=400, detail="Customer not found")
        logger.info(f"✅ Customer found: {customer.MaKH}")
        
        # 3. CHECK ROOM EXISTS AND AVAILABLE
        logger.info(f"🔍 Checking room with MaPhong={booking_data.MaPhong}")
        room_result = await db.execute(
            select(Room).where(Room.MaPhong == booking_data.MaPhong)
        )
        room = room_result.scalar_one_or_none()
        
        if not room:
            logger.warning(f"❌ Room not found: MaPhong={booking_data.MaPhong}")
            raise HTTPException(status_code=400, detail="Room not found")
        
        logger.info(f"📊 Room status: {room.TinhTrang}")
        if room.TinhTrang != 'Trống':
            logger.warning(f"❌ Room not available: status={room.TinhTrang}")
            raise HTTPException(status_code=400, detail="Room is not available")
        logger.info(f"✅ Room found and available: {room.MaPhong}")
        
        # 4. CHECK FOR BOOKING CONFLICTS (FIXED LOGIC)
        logger.info(f"🔍 Checking booking conflicts for room {booking_data.MaPhong}")
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
            logger.warning(f"❌ Room conflict: already booked from {conflicting_booking.NgayNhanPhong} to {conflicting_booking.NgayTraPhong}")
            raise HTTPException(
                status_code=400, 
                detail=f"Room is already booked from {conflicting_booking.NgayNhanPhong} to {conflicting_booking.NgayTraPhong}"
            )
        logger.info(f"✅ No booking conflicts found")
        
        # 5. CREATE BOOKING OBJECT
        logger.info("🛠️ Creating booking object...")
        booking_dict = booking_data.model_dump()
        
        # Add default fields if not present in schema
        if 'NgayDat' not in booking_dict:
            booking_dict['NgayDat'] = date.today()
            logger.info(f"➕ Added NgayDat: {booking_dict['NgayDat']}")
        
        if 'TrangThai' not in booking_dict:
            booking_dict['TrangThai'] = 'Đã đặt'
            logger.info(f"➕ Added TrangThai: {booking_dict['TrangThai']}")
        
        logger.info(f"🎯 Final booking data: {booking_dict}")
        
        booking = Booking(**booking_dict)
        db.add(booking)
        
        # 6. UPDATE ROOM STATUS
        logger.info(f"🔄 Updating room {room.MaPhong} status from '{room.TinhTrang}' to 'Đã đặt'")
        room.TinhTrang = 'Đã đặt'
        
        # 7. COMMIT TRANSACTION
        logger.info("💾 Committing to database...")
        await db.commit()
        await db.refresh(booking)
        
        logger.info(f"✅ Booking created successfully: MaDatPhong={booking.MaDatPhong}")
        return booking
        
    except HTTPException as http_err:
        # Re-raise HTTP exceptions
        logger.error(f"🚫 HTTP Exception: {http_err.detail}")
        raise http_err
        
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR in create_booking: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
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
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating booking {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{booking_id}")
async def cancel_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    try:
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
            logger.info(f"🔄 Room {room.MaPhong} status set to 'Trống'")
        
        booking.TrangThai = 'Hủy'
        await db.commit()
        
        logger.info(f"✅ Booking {booking_id} cancelled successfully")
        return {"message": "Booking cancelled successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error cancelling booking {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
