from dotenv import load_dotenv
import os

load_dotenv()

class Config():
    # CÁCH 1: Dùng SQLite luôn cho Railway
    # Bỏ comment dòng dưới để dùng SQLite 100%
    # DATABASE_URL = "sqlite+aiosqlite:///./hotel.db"
    # print("🚀 FORCE SQLITE ON RAILWAY")
    
    # CÁCH 2: Debug xem env variable có không
    print("=" * 40)
    print("DEBUG ENVIRONMENT:")
    print(f"DATABASE_URL in env: {'DATABASE_URL' in os.environ}")
    print(f"RAILWAY in env: {'RAILWAY' in os.environ}")
    print(f"RENDER in env: {'RENDER' in os.environ}")
    print("=" * 40)
    
    # Lấy DATABASE_URL từ env
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Nếu KHÔNG có DATABASE_URL từ Railway
    if not DATABASE_URL:
        print("❌ DATABASE_URL NOT FOUND IN ENVIRONMENT!")
        print("⚠️ Railway không inject biến môi trường")
        
        # Dùng SQLite cho chắc
        DATABASE_URL = "sqlite+aiosqlite:///./hotel.db"
        print("🔄 Fallback to SQLite")
        
        # Hoặc dùng PostgreSQL internal URL nếu biết
        # DATABASE_URL = "postgresql://postgres:yWBKcXapgaGvPyxFNFGWvrDYlxitJHjB@postgres.railway.internal:5432/railway"
    else:
        print(f"✅ DATABASE_URL found: {DATABASE_URL[:50]}...")
        
        # Convert PostgreSQL → asyncpg
        if DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            print("🔄 Converted to asyncpg")
    
    print(f"📦 Final DATABASE_URL: {DATABASE_URL[:50]}...")
    
    # JWT Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'temp-secret-key-change-me')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    
    # AWS (tạm bỏ)
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

config = Config()
