# app/schemas/post.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PostBase(BaseModel):
    title: str
    content: Optional[str] = None
    user: str
    time: datetime

    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    title: str
    content: Optional[str] = None
    user: str

    model_config = ConfigDict(from_attributes=True)

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Post(PostBase):
    id: int
    board_index: str  # DB의 외래키 컬럼 이름과 일치

    model_config = ConfigDict(from_attributes=True)
