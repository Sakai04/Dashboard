# app/models/board.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    board_index = Column(String, unique=True, index=True, nullable=False)

    # posts를 미리 로드하도록 설정 (eager loading)
    posts = relationship("Post", back_populates="board", cascade="all, delete-orphan", lazy="selectin")
