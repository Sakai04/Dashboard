# app/models/post.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    time = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
    user = Column(String, nullable=False)

    # board_id를 문자열로 선언하고, boards 테이블의 board_index를 참조
    board_index = Column(String, ForeignKey("boards.board_index"), nullable=True)

    board = relationship("Board", back_populates="posts")
