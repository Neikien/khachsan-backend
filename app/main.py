from fastapi import FastAPI
from fastapi.responses import JSONResponse  # ĐÚNG VỊ TRÍ
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import os
import uvicorn
import logging

# ==================== CONFIGURE LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🎯 MAIN.PY STARTING - RAILWAY DEPLOYMENT")
print("=" * 60)
print(f"Python version: {os.sys.version}")
print(f"Current directory: {os.getcwd()}")

from app.core.config import config
print(f"Config DATABASE_URL: {config.DATABASE_URL[:80] if config.DATABASE_URL else 'None'}")

# ==================== IMPORT ROUTERS ====================
try:
    print("🔧 Importing routers...")
    from app.controllers.auth import router as auth_router
    from app.controllers.hotel import router as hotel_router
    from app.controllers.room import router as room_router
    from app.controllers.booking import router as booking_router
    from app.controllers.customer import router as customer_router
    from app.controllers.service import router as service_router
    from app.controllers.chatbot_controller import router as chatbot_router
    print("✅ All routers imported successfully")
except Exception as e:
    print(f"❌ Error importing routers: {e}")
    import traceback
    traceback.print_exc()
    raise

# ==================== DATABASE INIT ====================
from app.core.database import engine, Base
from app.models import user, area, hotel, room, customer, booking, service, review, activity_log

app = FastAPI(
    title="Hotel Management API",
    description="Hệ thống quản lý khách sạn",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== CORS CONFIG ====================
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MIDDLEWARE FOR LOGGING ====================
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"🌐 {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"📊 {request.method} {request.url.path} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"💥 Error: {str(e)}")
        raise

# ==================== INCLUDE ROUTERS ====================
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(hotel_router, prefix='/hotels', tags=['Hotels'])
app.include_router(room_router, prefix='/rooms', tags=['Rooms'])
app.include_router(booking_router, prefix='/bookings', tags=['Bookings'])
app.include_router(customer_router, prefix='/customers', tags=['Customers'])
app.include_router(service_router, prefix='/services', tags=['Services'])
app.include_router(chatbot_router)

# ==================== DATABASE STARTUP ====================
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("🔗 Connecting to database...")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
        
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection test successful")
        
    except Exception as e:
        logger.error(f"⚠️ Database error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())

# ==================== ENDPOINTS ====================
@app.get('/')
async def root():
    return {
        "message": "Hotel Management API", 
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get('/health')
async def health_check():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            await result.fetchone()
        
        return {
            "status": "healthy", 
            "service": "hotel-management",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded", 
            "service": "hotel-management", 
            "database": "disconnected",
            "error": str(type(e).__name__)
        }

@app.get('/test')
async def test():
    return {"message": "API is working"}

# ==================== ERROR HANDLING ====================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"💥 Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# ==================== SERVER START ====================
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting server on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=port, 
        reload=False,
        log_level="info"
    )
