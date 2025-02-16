# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://username:password@localhost:5432/yourdbname"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

# FastAPI Dependency: 각 요청마다 AsyncSession 생성
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
