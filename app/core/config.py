from dotenv import load_dotenv
import os

load_dotenv()

class Config():
    # Database Configuration - FIXED FOR RAILWAY
    DATABASE_URL = os.getenv("DATABASE_URL")  # Railway cung cấp sẵn
    
    # Nếu không có DATABASE_URL (local dev), dùng MySQL
    if not DATABASE_URL:
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME', 'hotel_management')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print("💻 Using MySQL for local development")
    
    # Nếu là PostgreSQL (Railway), chuyển sang asyncpg
    if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        print("🚀 Using PostgreSQL asyncpg on Railway")
    
    print(f"📦 Final DATABASE_URL: {DATABASE_URL[:50]}..." if DATABASE_URL else "❌ No DATABASE_URL")
    
    # JWT Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'temp-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    
    # AWS S3 Configuration (tạm bỏ nếu không cần)
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    
    # Chỉ tạo S3 client nếu có credentials
    if AWS_ACCESS_KEY and AWS_SECRET_KEY:
        import boto3
        S3_CLIENT = boto3.client(
            service_name='s3',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
    else:
        S3_CLIENT = None
        print("⚠️ AWS S3 credentials not found")

config = Config()
