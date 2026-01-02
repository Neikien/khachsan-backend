from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# DEBUG NGAY ĐẦU
print("=" * 60)
print("🎯 MAIN.PY STARTING - RAILWAY DEPLOYMENT")
print("=" * 60)
print(f"Python version: {os.sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")
print(f"App directory: {os.listdir('app') if os.path.exists('app') else 'No app dir'}")
print(f"DATABASE_URL in env: {'DATABASE_URL' in os.environ}")
if 'DATABASE_URL' in os.environ:
    db_url = os.environ['DATABASE_URL']
    # Ẩn password
    if '@' in db_url:
        parts = db_url.split('@')
        user_part = parts[0]
        if ':' in user_part:
            user_pass = user_part.split(':')
            if len(user_pass) >= 3:  # postgres://user:pass@host
                safe_url = f"{user_pass[0]}:****@{parts[1]}"
            else:
                safe_url = db_url
        else:
            safe_url = db_url
    else:
        safe_url = db_url
    print(f"DATABASE_URL: {safe_url[:80]}...")
print("=" * 60)

# Import routers có sẵn của nhóm
from app.controllers.auth import router as auth_router
from app.controllers.hotel import router as hotel_router
from app.controllers.room import router as room_router
from app.controllers.booking import router as booking_router
from app.controllers.customer import router as customer_router
from app.controllers.service import router as service_router

# Import router của chatbot
from app.controllers.chatbot_controller import router as chatbot_router

# Import config để xem DATABASE_URL
from app.core.config import config
print(f"Config DATABASE_URL: {config.DATABASE_URL[:80] if config.DATABASE_URL else 'None'}")

from app.core.database import engine, Base
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
    "https://khachsan-backend.onrender.com",
    "*"  # Tạm thời cho dev
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

# Tạo database tables khi start - VỚI TRY-CATCH
@app.on_event("startup")
async def startup_event():
    try:
        print(f"🔗 Attempting to connect to database...")
        print(f"Database URL from engine: {str(engine.url)[:80]}...")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"⚠️ Database initialization error: {type(e).__name__}: {e}")
        print("📝 App will continue without database tables (they may already exist)")
        import traceback
        traceback.print_exc()

# Root endpoint
@app.get('/')
async def root():
    return {
        "message": "Hotel Management API", 
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Health check với database test
@app.get('/health')
async def health_check():
    try:
        # Test database connection
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            await result.fetchone()
        
        return {
            "status": "healthy", 
            "service": "hotel-management",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "degraded", 
            "service": "hotel-management", 
            "database": "disconnected",
            "error": str(type(e).__name__)
        }

# Simple test endpoint
@app.get('/test')
async def test():
    return {
        "message": "API is working",
        "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else "unknown"
    }

# Run với port từ Railway
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting server on port {port}")
    print(f"📖 API docs: http://localhost:{port}/docs")
    uvicorn.run(
        "main:app",  # Quan trọng: main:app chứ không phải app.main:app
        host="0.0.0.0", 
        port=port, 
        reload=False,  # Tắt reload trên production
        log_level="info"
    )
