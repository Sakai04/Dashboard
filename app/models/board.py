# app/models/board.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Board(Base):
    __tablename__ = "boards"

    board_index: str = Column(String, unique=True, index=True, nullable=False)

    # 연관된 게시글(Post)들 (Cascade 옵션으로 게시판 삭제 시 게시글도 삭제)
    posts = relationship("Post", back_populates="board", cascade="all, delete-orphan")
