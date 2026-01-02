from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.dependencies import get_db
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceUpdate
from app.models.service import Service

router = APIRouter()

@router.get("/", response_model=List[ServiceResponse])
async def get_services(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Service).offset(skip).limit(limit)
    )
    services = result.scalars().all()
    return services

@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Service).where(Service.MaDV == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=ServiceResponse)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db)
):
    service = Service(**service_data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Service).where(Service.MaDV == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    for field, value in service_data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    
    await db.commit()
    await db.refresh(service)
    return service

@router.delete("/{service_id}")
async def delete_service(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Service).where(Service.MaDV == service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    await db.delete(service)
    await db.commit()
    return {"message": "Service deleted successfully"}
