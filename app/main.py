from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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

# Import SYNC database components
from app.core.database import engine, Base, get_db
from app.core.config import config

# Import models để SQLAlchemy nhận biết
from app.models import user, area, hotel, room, customer, booking, service, review, activity_log

# THÊM DEBUG LOG NGAY ĐẦU
print("=" * 50)
print("🚀 STARTING APPLICATION ON RENDER")
print("=" * 50)
print(f"Environment DATABASE_URL exists: {'DATABASE_URL' in os.environ}")
print(f"Config DATABASE_URL: {config.DATABASE_URL[:50] if config.DATABASE_URL else 'None'}...")

app = FastAPI(
    title="Hotel Management API",
    description="Hệ thống quản lý khách sạn",
    version="1.0.0"
)

# CORS - ALLOW ALL FOR DEPLOYMENT
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://your-frontend.onrender.com",
    "*"
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

# Tạo database tables khi start - SYNC VERSION
@app.on_event("startup")
def startup_event():  # Bỏ async
    try:
        # Sử dụng config.DATABASE_URL
        safe_url = config.DATABASE_URL
        if safe_url and "://" in safe_url:
            protocol, rest = safe_url.split("://", 1)
            if "@" in rest:
                user_pass, host_db = rest.split("@", 1)
                if ":" in user_pass:
                    user, password = user_pass.split(":", 1)
                    safe_url = f"{protocol}://{user}:****@{host_db}"
        print(f"🔗 Connecting to database: {safe_url}")
        
        # SYNC create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print(f"Database URL from config: {config.DATABASE_URL}")
        print(f"Is PostgreSQL URL: {config.DATABASE_URL and 'postgresql' in config.DATABASE_URL}")
        import traceback
        traceback.print_exc()
        raise

# Root endpoint
@app.get('/')
def root():  # Bỏ async
    return {
        "message": "Hotel Management API", 
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check with database connectivity test - SYNC
@app.get('/health')
def health_check():  # Bỏ async
    try:
        # Test database connection SYNC
        with engine.connect() as conn:
            conn.execute("SELECT 1")
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
def debug_database():  # Bỏ async
    import re
    safe_url = config.DATABASE_URL
    if safe_url:
        # Hide password in URL
        safe_url = re.sub(r':([^:@]+)@', ':****@', safe_url)
    
    return {
        "database_url": safe_url,
        "database_type": "postgresql" if safe_url and "postgresql" in safe_url else "mysql",
        "environment": "render" if os.getenv("RENDER") else "local",
        "port": os.getenv("PORT", "8000")
    }

# Simple test endpoint
@app.get('/test')
def test_endpoint(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"message": "Database connection successful", "status": "ok"}
    except Exception as e:
        return {"message": "Database connection failed", "error": str(e)}, 500

# Run with Render port (10000)
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=port, 
        reload=False
    )
