from dotenv import load_dotenv
import os

load_dotenv()

class Config():
    # Database Configuration - FIXED
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Nếu không có DATABASE_URL (local dev), dùng MySQL
    if not DATABASE_URL:
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME', 'hotel_management')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Nếu là PostgreSQL (Render), chuyển sang asyncpg
    if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    # JWT Configuration (giữ nguyên)
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    
    # AWS (giữ nguyên)
    # ...

config = Config()
print(f"✅ DATABASE_URL: {config.DATABASE_URL[:50]}..." if config.DATABASE_URL else "❌ No DATABASE_URL")
