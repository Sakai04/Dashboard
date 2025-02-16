from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/board", tags=["board"])

@router.get("/", response_model=list[schemas.board.Board])
async def read_boards(db: AsyncSession = Depends(get_db)):
    boards = await crud.get_boards(db)
    return boards

@router.get("/{board_index}", response_model=schemas.board.Board)
async def read_board(board_index: str, db: AsyncSession = Depends(get_db)):
    board = await crud.get_board_by_index(db, board_index)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.post("/", response_model=schemas.board.Board)
async def create_new_board(board: schemas.board.BoardCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_board_by_index(db, board.board_index)
    if existing:
        raise HTTPException(status_code=400, detail="Board already exists")
    return await crud.create_board(db, board)

@router.put("/{board_index}", response_model=schemas.board.Board)
async def update_existing_board(board_index: str, board: schemas.board.BoardUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_board(db, board_index, board)
    if not updated:
        raise HTTPException(status_code=404, detail="Board not found")
    return updated

@router.delete("/{board_index}", response_model=schemas.board.Board)
async def delete_existing_board(board_index: str, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_board(db, board_index)
    if not deleted:
        raise HTTPException(status_code=404, detail="Board not found")
    return deleted
