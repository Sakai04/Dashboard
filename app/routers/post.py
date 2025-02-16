from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/post", tags=["post"])

@router.get("/{post_id}", response_model=schemas.post.Post)
async def read_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/board/{board_index}", response_model=list[schemas.post.Post])
async def read_posts_by_board(board_index: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    posts = await crud.get_posts_by_board(db, board_index, skip, limit)
    return posts

@router.post("/board/{board_index}", response_model=schemas.post.Post)
async def create_post_for_board(board_index: str, post: schemas.post.PostCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_post(db, post, board_index)


@router.put("/{post_id}", response_model=schemas.post.Post)
async def update_post(post_id: int, post: schemas.post.PostUpdate, db: AsyncSession = Depends(get_db)):
    updated_post = await crud.update_post(db, post_id, post)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post

@router.delete("/{post_id}", response_model=schemas.post.Post)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    deleted_post = await crud.delete_post(db, post_id)
    if not deleted_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return deleted_post
