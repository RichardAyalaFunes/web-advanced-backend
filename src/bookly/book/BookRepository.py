from datetime import datetime
from typing import List, Optional
from bookly.book.BookModel import Book
from .BooksDto import BookCreateDTO, BookUpdateDTO
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
import logging

logger = logging.getLogger(__name__)


class BooksRepository:
    """
    Servicio para gestionar operaciones CRUD de libros.
    """

    async def get_all_books(self, session: AsyncSession) -> List[Book]:
        """
        Obtiene todos los libros de la base de datos.

        Args:
            session: Sesión asíncrona de base de datos

        Returns:
            Lista de libros ordenados por fecha de creación descendente
        """
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_books_by_user(
        self, user_uid: str, session: AsyncSession
    ) -> List[Book]:
        """
        PENDIENTE REDACTAR
        """
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession) -> Optional[Book]:
        """
        Obtiene un libro por su identificador único.

        Args:
            book_uid: Identificador único del libro
            session: Sesión asíncrona de base de datos

        Returns:
            Libro encontrado o None si no existe
        """
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)

        if not result:
            logger.warning(f"Libro no encontrado con UID: {book_uid}")
            return None

        return result.first()

    async def create_book(
        self, book_data: BookCreateDTO, user_uid: str, session: AsyncSession
    ) -> Book:
        """
        Crea un nuevo libro en la base de datos.

        Args:
            book_data: Datos del libro a crear
            session: Sesión asíncrona de base de datos

        Returns:
            Libro creado
        """
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)

        logger.info(f"Libro creado en BD: {new_book.uid}")
        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdateDTO, session: AsyncSession
    ) -> Optional[Book]:
        """
        Actualiza un libro existente (actualización parcial).

        Args:
            book_uid: Identificador único del libro
            update_data: Datos a actualizar (solo campos proporcionados)
            session: Sesión asíncrona de base de datos

        Returns:
            Libro actualizado o None si no existe
        """
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            # Usar exclude_unset=True para solo actualizar campos proporcionados
            update_data_dict = update_data.model_dump(exclude_unset=True)

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            # Actualizar timestamp de modificación
            book_to_update.updated_at = datetime.now()

            await session.commit()
            await session.refresh(book_to_update)

            logger.info(f"Libro actualizado en BD: {book_uid}")
            return book_to_update
        else:
            logger.warning(f"Intento de actualizar libro inexistente: {book_uid}")
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession) -> Optional[dict]:
        """
        Elimina un libro de la base de datos.

        Args:
            book_uid: Identificador único del libro
            session: Sesión asíncrona de base de datos

        Returns:
            Diccionario vacío si se eliminó correctamente, None si no existe
        """
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete:
            session.delete(book_to_delete)
            await session.commit()
            logger.info(f"Libro eliminado de BD: {book_uid}")
            return {}

        logger.warning(f"Intento de eliminar libro inexistente: {book_uid}")
        return None
