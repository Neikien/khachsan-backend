from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
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

from app.core.database import engine, Base, DATABASE_URL  # Import DATABASE_URL
from app.models import user, area, hotel, room, customer, booking, service, review, activity_log

app = FastAPI(
    title="Hotel Management API",
    description="Hệ thống quản lý khách sạn",
    version="1.0.0"
)

# CORS - ALLOW ALL FOR DEPLOYMENT
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://your-frontend.onrender.com",  # Thêm frontend URL sau
    "*"  # Tạm thời cho development
]

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

# Tạo database tables khi start - FIXED FOR DEPLOYMENT
@app.on_event("startup")
async def startup_event():
    try:
        # Log database URL (ẩn password)
        safe_url = DATABASE_URL
        if "://" in DATABASE_URL:
            protocol, rest = DATABASE_URL.split("://", 1)
            if "@" in rest:
                user_pass, host_db = rest.split("@", 1)
                if ":" in user_pass:
                    user, password = user_pass.split(":", 1)
                    safe_url = f"{protocol}://{user}:****@{host_db}"
        print(f"🔗 Connecting to database: {safe_url}")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print(f"Database URL type: {type(DATABASE_URL)}")
        print(f"Database URL preview: {str(DATABASE_URL)[:50]}...")
        raise

# Root endpoint
@app.get('/')
async def root():
    return {
        "message": "Hotel Management API", 
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check with database connectivity test
@app.get('/health')
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {
            "status": "healthy", 
            "service": "hotel-management",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "service": "hotel-management",
            "database": "disconnected",
            "error": str(e)
        }, 503

# Debug endpoint
@app.get('/debug/database')
async def debug_database():
    import re
    safe_url = DATABASE_URL
    if DATABASE_URL:
        # Hide password in URL
        safe_url = re.sub(r':([^:@]+)@', ':****@', DATABASE_URL)
    
    return {
        "database_url_length": len(DATABASE_URL) if DATABASE_URL else 0,
        "database_url_preview": safe_url,
        "database_type": "postgresql" if DATABASE_URL and "postgresql" in DATABASE_URL else "mysql",
        "environment": os.getenv("RENDER", "local")
    }

# Run with Render port (10000)
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",  # Changed from "app.main:app" to "main:app"
        host="0.0.0.0", 
        port=port, 
        reload=False  # Disable reload for production
    )
