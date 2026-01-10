from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import config
import os

print("=" * 40)
print("🔧 DATABASE CONFIGURATION")
print("=" * 40)

# Debug: In ra DATABASE_URL để kiểm tra
print(f"Config DATABASE_URL: {config.DATABASE_URL}")

# Kiểm tra driver đang dùng
if config.DATABASE_URL:
    if 'postgresql+asyncpg://' in config.DATABASE_URL:
        print("✅ Using PostgreSQL asyncpg")
    elif 'mysql+aiomysql://' in config.DATABASE_URL:
        print("⚠️ Using MySQL aiomysql (might fail on Railway)")
    elif 'sqlite' in config.DATABASE_URL:
        print("💾 Using SQLite")
    else:
        print(f"🔍 Unknown driver in URL")

# SQLAlchemy base class
Base = declarative_base()

# FIX: Config khác nhau cho SQLite vs các database khác
if config.DATABASE_URL and 'sqlite' in config.DATABASE_URL:
    # SQLite: không dùng pool parameters
    engine = create_async_engine(
        config.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    print("⚙️ SQLite config: No connection pooling")
else:
    # FIX CHO RAILWAY POSTGRESQL: Thêm pool parameters hợp lý
    engine = create_async_engine(
        config.DATABASE_URL,
        echo=False,
        # THÊM CÁC THÔNG SỐ QUAN TRỌNG
        pool_size=3,           # Số connection tối thiểu trong pool
        max_overflow=2,        # Số connection tối đa khi vượt pool_size
        pool_pre_ping=True,    # Kiểm tra connection trước khi dùng
        pool_recycle=180,      # Tái sử dụng connection sau 3 phút (tránh timeout)
        pool_timeout=10,       # Timeout khi lấy connection
        connect_args={
            "command_timeout": 10,  # Timeout cho mỗi query
            "server_settings": {
                "statement_timeout": "10000"  # 10 giây timeout
            }
        }
    )
    print("⚙️ Railway PostgreSQL config: With optimized pooling")
    print(f"   • pool_size: 3")
    print(f"   • max_overflow: 2") 
    print(f"   • pool_recycle: 180s (3 phút)")
    print(f"   • pool_pre_ping: True")

# Async session
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    """Get database session với error handling"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
