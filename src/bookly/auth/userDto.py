from typing import List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
import uuid

from bookly.book.BooksDto import BookDTO
from bookly.reviews.reviewDto import ReviewDTO


class UserCreateDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., format="email", max_length=40)
    password: str = Field(..., min_length=8)
    role: str = Field(default="user")
    first_name: str = Field(..., min_length=1, max_length=20)
    last_name: str = Field(..., min_length=1, max_length=20)


class UserDTO(BaseModel):
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

    @field_validator("uid", mode="before")
    @classmethod
    def convert_uid_to_string(cls, value):
        """Convierte UUID a string si es necesario."""
        if isinstance(value, uuid.UUID):
            return str(value)
        return value


class UserBooksReviewsDTO(UserDTO):
    books: List[BookDTO]
    reviews: List[ReviewDTO]


class UserLoginDTO(BaseModel):
    email: str = Field(..., format="email", max_length=40)
    password: str = Field(..., min_length=8)


class EmailDTO(BaseModel):
    addresses: List[str]


class UserCreateResponseDTO(BaseModel):
    """
    DTO para la respuesta de creación de usuario.
    Incluye un mensaje informativo y los datos del usuario creado.
    """
    model_config = ConfigDict(from_attributes=True)
    
    message: str
    user: UserDTO


class UserVerifyResponseDTO(BaseModel):
    """
    DTO para la respuesta de verificación de usuario.
    Incluye un mensaje informativo y los datos del usuario verificado.
    """
    model_config = ConfigDict(from_attributes=True)
    
    message: str
    user: UserDTO

class PasswordResetRequestDTO(BaseModel):
    email: str
    
class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_password: str