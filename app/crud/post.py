# app/crud/post.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas

async def get_post(db: AsyncSession, post_id: int):
    stmt = select(models.Post).where(models.Post.id == post_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_posts_by_board(db: AsyncSession, board_id: int, skip: int = 0, limit: int = 100):
    stmt = select(models.Post).where(models.Post.board_id == board_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_post(db: AsyncSession, post: schemas.post.PostCreate, board_id: int):
    # 클라이언트에서 전달된 time은 무시하고 DB에서 자동 처리되도록 함
    post_data = post.model_dump()
    db_post = models.Post(
        title=post_data.get("title"),
        content=post_data.get("content"),
        user=post_data.get("user"),
        board_id=board_id
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

async def update_post(db: AsyncSession, post_id: int, post: schemas.post.PostUpdate):
    db_post = await get_post(db, post_id)
    if not db_post:
        return None
    update_data = post.model_dump(exclude_unset=True)
    # 클라이언트가 보낸 time 필드는 무시
    update_data.pop("time", None)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    await db.commit()
    await db.refresh(db_post)
    return db_post

async def delete_post(db: AsyncSession, post_id: int):
    db_post = await get_post(db, post_id)
    if not db_post:
        return None
    await db.delete(db_post)
    await db.commit()
    return db_post
