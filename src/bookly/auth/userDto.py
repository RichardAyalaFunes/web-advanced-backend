from typing import List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
import uuid

from bookly.book.BooksDto import BookModel

class UserCreateModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., format="email", max_length=40)
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")
    first_name:str = Field(..., min_length=1, max_length=20)
    last_name:str = Field(..., min_length=1, max_length=20)

class UserModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    uid: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    @field_validator('uid', mode='before')
    @classmethod
    def convert_uid_to_string(cls, value):
        """Convierte UUID a string si es necesario."""
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
    
class UserBooksModel(UserModel):
    books: List[BookModel]
    
    
class UserLoginModel(BaseModel):
    email: str = Field(..., format="email", max_length=40)
    password: str = Field(..., min_length=8)
