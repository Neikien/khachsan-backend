from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers có sẵn của nhóm
from app.controllers.auth import router as auth_router
from app.controllers.hotel import router as hotel_router
from app.controllers.room import router as room_router
from app.controllers.booking import router as booking_router
from app.controllers.customer import router as customer_router
from app.controllers.service import router as service_router

# Import router của chatbot
from app.controllers.chatbot_controller import router as chatbot_router

from app.core.database import engine, Base
from app.models import user, area, hotel, room, customer, booking, service, review, activity_log

app = FastAPI(
    title="Hotel Management API",
    description="Hệ thống quản lý khách sạn",
    version="1.0.0"
)

# CORS - SỬA PORT 3000
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers hệ thống quản lý
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(hotel_router, prefix='/hotels', tags=['Hotels'])
app.include_router(room_router, prefix='/rooms', tags=['Rooms'])
app.include_router(booking_router, prefix='/bookings', tags=['Bookings'])
app.include_router(customer_router, prefix='/customers', tags=['Customers'])
app.include_router(service_router, prefix='/services', tags=['Services'])

# Include router chatbot
app.include_router(chatbot_router)

# Tạo database tables khi start
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")

# Root endpoint
@app.get('/')
async def root():
    return {"message": "Hotel Management API", "version": "1.0.0"}

# Health check
@app.get('/health')
async def health_check():
    return {"status": "healthy", "service": "hotel-management"}

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)