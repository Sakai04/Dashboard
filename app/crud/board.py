# app/crud/board.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas

async def get_board(db: AsyncSession, board_id: int):
    stmt = select(models.Board).where(models.Board.id == board_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_board_by_index(db: AsyncSession, board_index: str):
    stmt = select(models.Board).where(models.Board.board_index == board_index)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_boards(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(models.Board).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_board(db: AsyncSession, board: schemas.board.BoardCreate):
    db_board = models.Board(board_index=board.board_index)
    db.add(db_board)
    await db.commit()
    await db.refresh(db_board)
    return db_board

async def update_board(db: AsyncSession, board_id: int, board: schemas.board.BoardUpdate):
    db_board = await get_board(db, board_id)
    if not db_board:
        return None
    update_data = board.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_board, key, value)
    await db.commit()
    await db.refresh(db_board)
    return db_board

async def delete_board(db: AsyncSession, board_id: int):
    db_board = await get_board(db, board_id)
    if not db_board:
        return None
    await db.delete(db_board)
    await db.commit()
    return db_board
