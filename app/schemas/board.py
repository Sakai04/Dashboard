# app/schemas/board.py
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.post import Post

class BoardBase(BaseModel):
    board_index: str

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BaseModel):
    board_index: Optional[str] = None

class Board(BoardBase):
    posts: List[Post] = []

    model_config = ConfigDict(from_attributes=True)
