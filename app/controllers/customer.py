from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.dependencies import get_db
from app.schemas.customer import CustomerResponse, CustomerCreate, CustomerUpdate
from app.models.customer import Customer

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Customer).offset(skip).limit(limit)
    )
    customers = result.scalars().all()
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Customer).where(Customer.MaKH == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Customer).where(Customer.MaKH == customer_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for field, value in customer_data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    
    await db.commit()
    await db.refresh(customer)
    return customer
