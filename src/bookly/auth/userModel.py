from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlmodel import Relationship, SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid

if TYPE_CHECKING:
    from bookly.reviews.reviewModel import Review
    from bookly.book.BookModel import Book


class User(SQLModel, table=True):
    """
    Modelo de usuario para el sistema de autenticación.

    Attributes:
        uid: Identificador único del usuario
        username: Nombre de usuario único
        email: Correo electrónico del usuario
        first_name: Nombre del usuario
        last_name: Apellido del usuario
        role: Rol del usuario (default: "user")
        is_verified: Indica si el usuario ha verificado su email
        password_hash: Hash de la contraseña del usuario
        created_at: Fecha de creación del usuario
        updated_at: Fecha de última actualización
    """

    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # Associated entities
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<User {self.username}>"
