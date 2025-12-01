from uuid import UUID, uuid4
from sqlalchemy.dialects import postgresql as pg
from sqlmodel import Field, Column, SQLModel, Relationship
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from bookly.book.BookModel import Book 

class BookTag(SQLModel, table=True):
    book_id: UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"