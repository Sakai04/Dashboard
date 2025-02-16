# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import board_router, post_router

app = FastAPI(title="Backend API for BoardPost")

# CORS 미들웨어 추가: React 앱이 실행되는 도메인을 명시하거나, 모든 도메인을 허용할 수 있습니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버가 기본적으로 이 주소에서 실행됩니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(board_router)
app.include_router(post_router)
