from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate

# board_index(문자열)을 기준으로 Board 조회
async def get_board_by_index(db: AsyncSession, board_index: str):
    stmt = select(Board).options(selectinload(Board.posts)).where(Board.board_index == board_index)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# 모든 Board 조회
async def get_boards(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Board).options(selectinload(Board.posts)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_board(db: AsyncSession, board: BoardCreate):
    db_board = Board(board_index=board.board_index)
    db.add(db_board)
    await db.commit()
    await db.refresh(db_board)
    return db_board

async def update_board(db: AsyncSession, board_index: str, board_update: BoardUpdate):
    db_board = await get_board_by_index(db, board_index)
    if not db_board:
        return None
    update_data = board_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_board, key, value)
    await db.commit()
    await db.refresh(db_board)
    return db_board

async def delete_board(db: AsyncSession, board_index: str):
    db_board = await get_board_by_index(db, board_index)
    if not db_board:
        return None
    await db.delete(db_board)
    await db.commit()
    return db_board
