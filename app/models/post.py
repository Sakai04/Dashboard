# app/models/post.py
import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String, nullable=False)
    # content는 선택적 필드
    content: str = Column(String, nullable=True)
    # 작성 시 현재 UTC 시간, 수정 시 자동 갱신
    time: datetime.datetime = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
    user: str = Column(String, nullable=False)

    board_id: int = Column(Integer, ForeignKey("boards.id"), nullable=False)
    board = relationship("Board", back_populates="posts")
