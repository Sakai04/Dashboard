# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import board_router, post_router
from app.models import models, Post, Board
from app.database import engine, Base, AsyncSessionLocal
from sqlalchemy import select

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
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 기본 board 목록: 기본키로 사용할 문자열들
    default_boards = ["Free", "HN", "Front", "Back"]

    # AsyncSession을 사용하여 기본 board들이 존재하는지 확인하고, 없으면 추가
    async with AsyncSessionLocal() as session:
        for board_id in default_boards:
            result = await session.execute(
                select(Board).where(Board.board_index == board_id)
            )
            board = result.scalar_one_or_none()
            if not board:
                session.add(Board(board_index=board_id))
        await session.commit()


app.include_router(board_router)
app.include_router(post_router)
