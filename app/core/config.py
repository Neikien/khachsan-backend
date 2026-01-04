from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        DATABASE_URL = "sqlite+aiosqlite:///./hotel.db"
    else:
        if DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )

    REFRESH_TOKEN_EXPIRE_DAYS = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY", "temp-secret-key-change-me"
    )
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    
    # THÊM DÒNG NÀY CHO CHATBOT
    CHATBOT_API_KEY = os.getenv("apikey")  # Lấy từ biến 'apikey' trên Railway

config = Config()
