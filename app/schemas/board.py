from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.schemas.post import Post  # Post 응답 스키마

class BoardBase(BaseModel):
    board_index: str

    model_config = ConfigDict(from_attributes=True)

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BaseModel):
    board_index: Optional[str] = None
    # 추가 업데이트할 필드가 있으면 여기에 추가

    model_config = ConfigDict(from_attributes=True)

class Board(BoardBase):
    posts: List[Post] = []

    model_config = ConfigDict(from_attributes=True)
