from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.dependencies import get_db
from app.schemas.room import RoomResponse, RoomCreate, RoomUpdate
from app.models.room import Room
from app.models.hotel import Hotel

router = APIRouter()

@router.get("/", response_model=List[RoomResponse])
async def get_rooms(
    hotel_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Room)
    if hotel_id:
        query = query.where(Room.MaKS == hotel_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    rooms = result.scalars().all()
    return rooms

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Room).where(Room.MaPhong == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.post("/", response_model=RoomResponse)
async def create_room(room_data: RoomCreate, db: AsyncSession = Depends(get_db)):
    # Check if hotel exists
    hotel_result = await db.execute(
        select(Hotel).where(Hotel.MaKS == room_data.MaKS)
    )
    hotel = hotel_result.scalar_one_or_none()
    
    if not hotel:
        raise HTTPException(status_code=400, detail="Hotel not found")
    
    room = Room(**room_data.model_dump())
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room

@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Room).where(Room.MaPhong == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    for field, value in room_data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    
    await db.commit()
    await db.refresh(room)
    return room

@router.delete("/{room_id}")
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Room).where(Room.MaPhong == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    await db.delete(room)
    await db.commit()
    return {"message": "Room deleted successfully"}
