from datetime import datetime
from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
import uuid

class User(SQLModel, table=True):
    """
    Modelo de usuario para el sistema de autenticación.
    
    Attributes:
        uid: Identificador único del usuario
        username: Nombre de usuario único
        email: Correo electrónico del usuario
        first_name: Nombre del usuario
        last_name: Apellido del usuario
        is_verified: Indica si el usuario ha verificado su email
        created_at: Fecha de creación del usuario
        updated_at: Fecha de última actualización
    """
    __tablename__ = "users"
    
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<User {self.username}>"