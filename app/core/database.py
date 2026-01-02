import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import config

print(f"🔧 Database URL from config: {config.DATABASE_URL[:50] if config.DATABASE_URL else 'None'}...")

# FIX: Convert PostgreSQL URL cho psycopg2 (SYNC)
if config.DATABASE_URL and config.DATABASE_URL.startswith("postgresql://"):
    # Render PostgreSQL → psycopg2 (SYNC)
    DATABASE_URL = config.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    print(f"🔄 Converted to sync PostgreSQL URL (psycopg2)")
elif config.DATABASE_URL and config.DATABASE_URL.startswith("mysql://"):
    # MySQL → pymysql (SYNC)
    DATABASE_URL = config.DATABASE_URL.replace("mysql://", "mysql+pymysql://")
    print(f"🔄 Converted to sync MySQL URL")
else:
    DATABASE_URL = config.DATABASE_URL

print(f"📦 Final Database URL: {DATABASE_URL[:50]}...")

# SQLAlchemy base class
Base = declarative_base()

# Database engine SYNC
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
)

# SYNC session (không còn AsyncSession)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# SYNC dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
