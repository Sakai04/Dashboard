# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic_settings import BaseSettings

# 환경 변수 설정
class DatabaseSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_NAME: str = "mydb"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

db_settings = DatabaseSettings()

# SSL 인증서 경로 확인 (절대경로 권장)
SSL_ROOT_CERT = os.path.abspath("./certs/rds-ca-2019-root.pem")
if not os.path.exists(SSL_ROOT_CERT):
    raise FileNotFoundError(f"SSL certificate not found: {SSL_ROOT_CERT}")

# 데이터베이스 엔진 설정
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{db_settings.DB_USER}:{db_settings.DB_PASSWORD}@"
    f"{db_settings.DB_HOST}:5432/"
    f"{db_settings.DB_NAME}?"
    f"ssl=require&sslrootcert={SSL_ROOT_CERT}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# 의존성 주입 설정
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
