import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel


class TagDTO(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime


class TagCreateDTO(BaseModel):
    name: str


class TagAddDTO(BaseModel):
    tags: List[TagCreateDTO]