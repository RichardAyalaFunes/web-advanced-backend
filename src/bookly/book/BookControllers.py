from fastapi import APIRouter, status, Depends
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from .BooksDto import Book, BookUpdateModel, BookCreateModel
from .exceptions import BooklyException
from bookly.book.BookService import BookService
from bookly.db.main import get_session
from bookly.auth.dependencies import AccessTokenBearer

logger = logging.getLogger(__name__)

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@book_router.get("/", response_model=List[Book])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    user_details=Depends(access_token_bearer),
) -> List[Book]:
    """
    Obtiene todos los libros del sistema.

    Args:
        session: Sesión de base de datos

    Returns:
        List[Book]: Lista de todos los libros

    Raises:
        BooklyException: Si ocurre un error al obtener los libros
    """
    try:
        logger.info("Obteniendo todos los libros")
        books = await book_service.get_all_books(session)
        logger.info(f"Se encontraron {len(books)} libros")
        return books
    except Exception as e:
        logger.error(f"Error al obtener libros: {str(e)}")
        raise BooklyException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error al obtener libros",
            detail=str(e),
            error_code="FETCH_ERROR",
        )


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(
    book_data: BookCreateModel, session: AsyncSession = Depends(get_session)
) -> Book:
    """
    Crea un nuevo libro en el sistema.

    Args:
        book_data: Datos del libro a crear
        session: Sesión de base de datos

    Returns:
        Book: Libro creado

    Raises:
        BooklyException: Si ocurre un error durante la creación
    """
    try:
        logger.info(f"Creando libro: {book_data.title}")
        new_book = await book_service.create_book(book_data, session)
        logger.info(f"Libro creado exitosamente: {new_book.uid}")
        return new_book

    except ValueError as ve:
        logger.error(f"Error de validación al crear libro: {str(ve)}")
        raise BooklyException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Error de datos",
            detail=str(ve),
            error_code="DATA_ERROR",
        )
    except Exception as e:
        logger.error(f"Error no identificado al crear libro: {str(e)}")
        raise BooklyException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error interno del servidor",
            detail=str(e),
            error_code="INTERNAL_SERVER_ERROR",
        )


@book_router.get("/{book_uid}", response_model=Book)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session)) -> Book:
    """
    Obtiene un libro por su identificador único.

    Args:
        book_uid: Identificador único del libro
        session: Sesión de base de datos

    Returns:
        Book: Libro encontrado

    Raises:
        BooklyException: Si el libro no existe
    """
    logger.info(f"Buscando libro con UID: {book_uid}")
    try:
        book = await book_service.get_book(book_uid, session)

        if book:
            logger.info(f"Libro encontrado: {book.title}")
            return book
        else:
            logger.warning(f"Libro no encontrado con UID: {book_uid}")
            raise BooklyException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Libro no encontrado",
                detail=f"No existe un libro con el UID: {book_uid}",
                error_code="BOOK_NOT_FOUND",
            )
    except Exception as e:
        logger.error(f"Error al buscar libro: {str(e)}")
        raise BooklyException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error al buscar libro",
            detail=str(e),
            error_code="FETCH_ERROR",
        )


@book_router.patch("/{book_uid}", response_model=Book)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
) -> Book:
    """
    Actualiza un libro existente.

    Args:
        book_uid: Identificador único del libro
        book_update_data: Datos a actualizar del libro
        session: Sesión de base de datos

    Returns:
        Book: Libro actualizado

    Raises:
        BooklyException: Si el libro no existe
    """
    logger.info(f"Actualizando libro con UID: {book_uid}")

    try:
        updated_book = await book_service.update_book(
            book_uid, book_update_data, session
        )
        if updated_book:
            logger.info(f"Libro actualizado exitosamente: {book_uid}")
            return updated_book
        else:
            logger.warning(f"No se pudo actualizar, libro no encontrado: {book_uid}")
            raise BooklyException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Libro no encontrado",
                detail=f"No existe un libro con el UID: {book_uid}",
                error_code="BOOK_NOT_FOUND",
            )
    except Exception as e:
        logger.error(f"Error al actualizar libro: {str(e)}")
        raise BooklyException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error al actualizar libro",
            detail=str(e),
            error_code="UPDATE_ERROR",
        )


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_uid: str, session: AsyncSession = Depends(get_session)
) -> None:
    """
    Elimina un libro del sistema.

    Args:
        book_uid: Identificador único del libro
        session: Sesión de base de datos

    Returns:
        None

    Raises:
        BooklyException: Si el libro no existe
    """
    logger.info(f"Eliminando libro con UID: {book_uid}")

    try:
        await book_service.delete_book(book_uid, session)
        logger.info(f"Libro eliminado exitosamente: {book_uid}")
        return None

    except Exception as e:
        logger.error(f"Error al eliminar libro: {str(e)}")
        raise BooklyException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Error al eliminar libro",
            detail=str(e),
            error_code="DELETE_ERROR",
        )
