from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base


class Board(Base):
    __tablename__ = "boards"

    # board_index를 기본키로 사용 (예: "Free", "HN", "Front", "Back")
    board_index = Column(String, primary_key=True, index=True, nullable=False)

    # Board와 Post 간의 관계 설정 (posts는 lazy 로딩 또는 eager 로딩 설정 가능)
    posts = relationship("Post", back_populates="board", cascade="all, delete-orphan")
