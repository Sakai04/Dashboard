# app/main.py
import asyncio

from app.routers import board_router, post_router

from fastapi import FastAPI
from app.database import engine, Base

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 라우터 포함 등 추가 설

app.include_router(board_router)
app.include_router(post_router)
