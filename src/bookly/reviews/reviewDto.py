from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class ReviewDTO(BaseModel):
    uid: UUID
    rating: int
    review_text: str
    user_uid: Optional[UUID]
    book_uid: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class ReviewCreateDTO(BaseModel):
    rating: int
    review_text: str
