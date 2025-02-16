# app/crud/post.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import Post
from app.models.board import Board
from app import schemas

async def get_post(db: AsyncSession, post_id: int):
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_posts_by_board(db: AsyncSession, board_index: str, skip: int = 0, limit: int = 100):
    # board_index 컬럼을 기준으로 게시글 조회
    stmt = select(Post).where(Post.board_index == board_index).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_post(db: AsyncSession, post: schemas.post.PostCreate, board_index: str):
    # 지정된 board_index를 사용하여 게시글 생성
    post_data = post.model_dump() if hasattr(post, "model_dump") else post
    db_post = Post(
        title=post_data.get("title"),
        content=post_data.get("content"),
        user=post_data.get("user"),
        board_index=board_index  # 외래키를 board_index로 설정
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
    # 클라이언트가 보낸 time 필드는 무시합니다.
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
