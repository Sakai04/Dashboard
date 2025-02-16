# app/main.py
import asyncio
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import board_router, post_router

app = FastAPI(title="Backend API for BoardPost")

# 개발용: 앱 시작 시 데이터베이스 테이블 생성
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())

app.include_router(board_router)
app.include_router(post_router)
