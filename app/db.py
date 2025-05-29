# DB connection setup
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Tải biến môi trường từ .env
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Tạo Async Engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Tạo Async SessionLocal
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Dependency để lấy Async Database Session
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()