from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import config

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
    # PostgreSQL/MySQL: dùng pool NHƯNG KHÔNG có pool_size, max_overflow
    engine = create_async_engine(
        config.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
        # KHÔNG CÓ pool_size và max_overflow!
    )
    print("⚙️ Database config: With basic pooling (no pool_size/max_overflow)")

# Async session
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
