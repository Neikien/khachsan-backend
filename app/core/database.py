import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import config

# Log để debug
print(f"🔧 Database URL from config: {config.DATABASE_URL[:50] if config.DATABASE_URL else 'None'}...")

# FIX: Convert PostgreSQL URL cho asyncpg
if config.DATABASE_URL and config.DATABASE_URL.startswith("postgresql://"):
    # Render PostgreSQL → asyncpg
    DATABASE_URL = config.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    print(f"🔄 Converted to async PostgreSQL URL")
elif config.DATABASE_URL and config.DATABASE_URL.startswith("mysql://"):
    # MySQL → aiomysql
    DATABASE_URL = config.DATABASE_URL.replace("mysql://", "mysql+aiomysql://")
    print(f"🔄 Converted to async MySQL URL")
else:
    DATABASE_URL = config.DATABASE_URL

print(f"📦 Final Database URL: {DATABASE_URL[:50]}...")

# SQLAlchemy base class
Base = declarative_base()

# Database engine với retry logic
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
)

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
