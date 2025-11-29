from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class BookModel(BaseModel):
    """
    Modelo de dominio para representar un libro.
    
    Attributes:
        id: Identificador único del libro
        title: Título del libro
        author: Autor(es) del libro
        publisher: Editorial del libro
        published_date: Fecha de publicación (formato: YYYY-MM-DD)
        page_count: Número de páginas
        language: Idioma del libro
    """
    uid: UUID = Field(..., description="Identificador único del libro")
    title: str = Field(..., min_length=1, description="Título del libro")
    author: str = Field(..., min_length=1, description="Autor(es) del libro")
    publisher: str = Field(..., min_length=1, description="Editorial del libro")
    published_date: str = Field(..., description="Fecha de publicación (YYYY-MM-DD)")
    page_count: int = Field(..., gt=0, description="Número de páginas")
    language: str = Field(..., min_length=1, description="Idioma del libro")
    created_at: datetime
    updated_at: datetime

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    # user_uid: Optional[str]

class BookUpdateModel(BaseModel):
    """
    Modelo para actualizar información de un libro existente (PATCH).
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Attributes:
        title: Título del libro (opcional)
        author: Autor(es) del libro (opcional)
        publisher: Editorial del libro (opcional)
        published_date: Fecha de publicación (opcional)
        page_count: Número de páginas (opcional)
        language: Idioma del libro (opcional)
    """
    title: Optional[str] = Field(None, min_length=1, description="Título del libro")
    author: Optional[str] = Field(None, min_length=1, description="Autor(es) del libro")
    publisher: Optional[str] = Field(None, min_length=1, description="Editorial del libro")
    published_date: Optional[str] = Field(None, description="Fecha de publicación (YYYY-MM-DD)")
    page_count: Optional[int] = Field(None, gt=0, description="Número de páginas")
    language: Optional[str] = Field(None, min_length=1, description="Idioma del libro")
