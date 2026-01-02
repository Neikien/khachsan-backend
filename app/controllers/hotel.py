from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.dependencies import get_db
from app.schemas.hotel import HotelResponse, HotelCreate, HotelUpdate
from app.models.hotel import Hotel
from app.models.area import Area

router = APIRouter()

@router.get("/", response_model=List[HotelResponse])
async def get_hotels(
    skip: int = 0, 
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Hotel).offset(skip).limit(limit)
    )
    hotels = result.scalars().all()
    return hotels

@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Hotel).where(Hotel.MaKS == hotel_id)
    )
    hotel = result.scalar_one_or_none()
    
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.post("/", response_model=HotelResponse)
async def create_hotel(hotel_data: HotelCreate, db: AsyncSession = Depends(get_db)):
    # Check if area exists
    area_result = await db.execute(
        select(Area).where(Area.MaKhuVuc == hotel_data.MaKhuVuc)
    )
    area = area_result.scalar_one_or_none()
    
    if not area:
        raise HTTPException(status_code=400, detail="Area not found")
    
    hotel = Hotel(**hotel_data.model_dump())
    db.add(hotel)
    await db.commit()
    await db.refresh(hotel)
    return hotel

@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int, 
    hotel_data: HotelUpdate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Hotel).where(Hotel.MaKS == hotel_id)
    )
    hotel = result.scalar_one_or_none()
    
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    # Update fields
    for field, value in hotel_data.model_dump(exclude_unset=True).items():
        setattr(hotel, field, value)
    
    await db.commit()
    await db.refresh(hotel)
    return hotel

@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Hotel).where(Hotel.MaKS == hotel_id)
    )
    hotel = result.scalar_one_or_none()
    
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    await db.delete(hotel)
    await db.commit()
    return {"message": "Hotel deleted successfully"}
