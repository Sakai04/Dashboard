# app/routers/post.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.post("/board/{board_id}", response_model=schemas.post.Post)
async def create_post_for_board(
    board_id: int,
    post: schemas.post.PostCreate,
    db: AsyncSession = Depends(get_db)
):
    # 게시판 존재 여부 확인
    board = await crud.board.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    # 게시글 생성
    return await crud.post.create_post(db, post, board_id)

@router.get("/board/{board_id}", response_model=List[schemas.post.Post])
async def read_posts_by_board(
    board_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    board = await crud.board.get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return await crud.post.get_posts_by_board(db, board_id, skip, limit)

@router.get("/{post_id}", response_model=schemas.post.Post)
async def read_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    post = await crud.post.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=schemas.post.Post)
async def update_post(
    post_id: int,
    post: schemas.post.PostUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_post = await crud.post.update_post(db, post_id, post)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post

@router.delete("/{post_id}", response_model=schemas.post.Post)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted_post = await crud.post.delete_post(db, post_id)
    if not deleted_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return deleted_post
