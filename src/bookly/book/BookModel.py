from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from bookly.auth.userModel import User

class Book(SQLModel, table=True):
    __tablename__ = "books"
    
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    user: Optional["User"] = Relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"