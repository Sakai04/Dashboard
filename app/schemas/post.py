# app/schemas/post.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# 공통 기본 스키마 (응답에 사용)
class PostBase(BaseModel):
    title: str
    content: Optional[str] = None
    user: str
    time: datetime  # DB에서 자동으로 설정됨

    model_config = ConfigDict(from_attributes=True)

# POST 요청 시 사용할 스키마 (time 필드 제외)
class PostCreate(BaseModel):
    title: str
    content: Optional[str] = None
    user: str

    model_config = ConfigDict(from_attributes=True)

# 업데이트 요청 시 사용할 스키마 (모든 필드는 선택적)
class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# 응답용 스키마: DB에서 가져온 데이터를 직렬화할 때 사용
class Post(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
