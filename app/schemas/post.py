# app/schemas/post.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PostBase(BaseModel):
    title: str
    # content는 선택적
    content: Optional[str] = None
    time: datetime
    user: str

class PostCreate(PostBase):
    # 클라이언트가 time을 전달하지 않도록 할 수 있음;
    # 서버에서 default와 onupdate로 처리하므로, 여기서는 선택적일 수도 있습니다.
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    # time 필드는 업데이트 시 무시됨
    time: Optional[datetime] = None
    user: Optional[str] = None

class Post(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
