# app/routers/board.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/boards",
    tags=["boards"],
)

@router.get("/", response_model=List[schemas.board.Board])
async def read_boards(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    boards = await crud.board.get_boards(db, skip=skip, limit=limit)
    return boards

@router.get("/{board_id}", response_model=schemas.board.Board)
async def read_board(board_id: int, db: AsyncSession = Depends(get_db)):
    board = await crud.board.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.post("/", response_model=schemas.board.Board)
async def create_new_board(board: schemas.board.BoardCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.board.get_board_by_index(db, board.board_index)
    if existing:
        raise HTTPException(status_code=400, detail="Board already exists")
    return await crud.board.create_board(db, board)

@router.put("/{board_id}", response_model=schemas.board.Board)
async def update_existing_board(board_id: int, board: schemas.board.BoardUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud.board.update_board(db, board_id, board)
    if not updated:
        raise HTTPException(status_code=404, detail="Board not found")
    return updated

@router.delete("/{board_id}", response_model=schemas.board.Board)
async def delete_existing_board(board_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.board.delete_board(db, board_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Board not found")
    return deleted
