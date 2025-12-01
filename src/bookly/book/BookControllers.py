from fastapi import APIRouter, status, Depends
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from .BooksDto import BookDTO, BookUpdateDTO, BookCreateDTO, BookReviewsDTO
from bookly.errors import BookNotFound, BooklyException
from bookly.book.BookRepository import BooksRepository
from bookly.db.main import get_session
from bookly.auth.dependencies import AccessTokenBearer, RoleChecker

logger = logging.getLogger(__name__)

book_router = APIRouter()
book_service = BooksRepository()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get("/", response_model=List[BookDTO], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict =Depends(access_token_bearer),
) -> List[BookDTO]:
    """
    Obtiene todos los libros del sistema.

    Args:
        session: Sesión de base de datos

    Returns:
        List[Book]: Lista de todos los libros

    Raises:
        BooklyException: Si ocurre un error al obtener los libros
    """
    print(token_details)
    try:
        logger.info("Obteniendo todos los libros")
        books = await book_service.get_all_books(session)
        logger.info(f"Se encontraron {len(books)} libros")
        return books
    except Exception as e:
        logger.error(f"Error al obtener libros: {str(e)}")
        raise BooklyException(f"Error al obtener libros: {str(e)}")


@book_router.get("/user/{user_uid}", response_model=List[BookDTO], dependencies=[role_checker])
async def get_books_by_user(
    user_uid: str, 
    session: AsyncSession = Depends(get_session),
    token_details: dict =Depends(access_token_bearer),
) -> List[BookDTO]:
    """ PENDIENTE REDACTAR """
    print(token_details)
    try:
        logger.info("Obteniendo todos los libros")
        books = await book_service.get_books_by_user(user_uid, session)
        logger.info(f"Se encontraron {len(books)} libros")
        return books
    except Exception as e:
        logger.error(f"Error al obtener libros: {str(e)}")
        raise BooklyException(f"Error al obtener libros: {str(e)}")


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BookDTO,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateDTO,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> BookDTO:
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
        user_uid = token_details.get('user')['user_uid']

        new_book = await book_service.create_book(book_data, user_uid, session)
        logger.info(f"Libro creado exitosamente: {new_book.uid}")
        return new_book

    except ValueError as ve:
        logger.error(f"Error de validación al crear libro: {str(ve)}")
        raise BooklyException(f"Error de datos: {str(ve)}")
    except Exception as e:
        logger.error(f"Error no identificado al crear libro: {str(e)}")
        raise BooklyException(f"Error interno del servidor: {str(e)}")


@book_router.get("/{book_uid}", response_model=BookReviewsDTO, dependencies=[role_checker])
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict =Depends(access_token_bearer),
) -> BookDTO:
    """
    Obtiene un libro por su identificador único.

    Args:
        book_uid: Identificador único del libro
        session: Sesión de base de datos

    Returns:
        Book: Libro encontrado

    Raises:
        BookNotFound: Si el libro no existe
        BooklyException: Si ocurre un error al buscar el libro
    """
    logger.info(f"Buscando libro con UID: {book_uid}")
    try:
        book = await book_service.get_book(book_uid, session)

        if book:
            logger.info(f"Libro encontrado: {book.title}")
            return book
        else:
            logger.warning(f"Libro no encontrado con UID: {book_uid}")
            raise BookNotFound(f"No existe un libro con el UID: {book_uid}")
    except BookNotFound:
        raise
    except Exception as e:
        logger.error(f"Error al buscar libro: {str(e)}")
        raise BooklyException(f"Error al buscar libro: {str(e)}")


@book_router.patch("/{book_uid}", response_model=BookDTO, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateDTO,
    session: AsyncSession = Depends(get_session),
    token_details: dict =Depends(access_token_bearer),
) -> BookDTO:
    """
    Actualiza un libro existente.

    Args:
        book_uid: Identificador único del libro
        book_update_data: Datos a actualizar del libro
        session: Sesión de base de datos

    Returns:
        Book: Libro actualizado

    Raises:
        BookNotFound: Si el libro no existe
        BooklyException: Si ocurre un error al buscar el libro
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
            raise BookNotFound(f"No existe un libro con el UID: {book_uid}")
    except BookNotFound:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar libro: {str(e)}")
        raise BooklyException(f"Error al actualizar libro: {str(e)}")


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict =Depends(access_token_bearer),
) -> None:
    """
    Elimina un libro del sistema.

    Args:
        book_uid: Identificador único del libro
        session: Sesión de base de datos

    Returns:
        None

    Raises:
        BookNotFound: Si el libro no existe
        BooklyException: Si ocurre un error al buscar el libro
    """
    logger.info(f"Eliminando libro con UID: {book_uid}")

    try:
        await book_service.delete_book(book_uid, session)
        logger.info(f"Libro eliminado exitosamente: {book_uid}")
        return None
    except BookNotFound:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar libro: {str(e)}")
        raise BooklyException(f"Error al eliminar libro: {str(e)}")
