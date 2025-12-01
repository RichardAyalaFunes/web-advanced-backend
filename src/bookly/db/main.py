"""
Configuración del motor de base de datos.

Este módulo crea y configura el motor de base de datos
utilizando SQLModel y SQLAlchemy con soporte asíncrono.
"""
from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from bookly.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Importar modelos para que SQLModel los registre en metadata
from bookly.book.BookModel import Book
from bookly.auth.userModel import User
from bookly.reviews.reviewModel import Review

# Crear el motor de base de datos usando la URL desde configuración
# * Conexión Síncrona (comentada)
# engine = create_engine(settings.DATABASE_URL, echo=True)

# * Conexión Asíncrona - LAZY INITIALIZATION
engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """
    Obtiene el motor de base de datos, creándolo si es necesario.
    
    Returns:
        AsyncEngine: Motor de base de datos configurado
    """
    global engine
    if engine is None:
        engine = AsyncEngine(
            create_engine(url=settings.DATABASE_URL, echo=False)
        )
    return engine

async def init_db() -> None:
    """
    Inicializa la conexión a la base de datos y crea las tablas.
    
    Esta función se ejecuta durante el startup de la aplicación
    para crear las tablas necesarias en la base de datos.
    """
    try:
        logger.info("Inicializando base de datos...")
        # Debug: mostrar la URL de conexión (ocultando password)
        db_url_display = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
        logger.info(f"Conectando a: {db_url_display}")
        
        # Obtener el motor de base de datos
        db_engine = get_engine()
        
        async with db_engine.begin() as conn:
            # Crear todas las tablas definidas en los modelos
            await conn.run_sync(SQLModel.metadata.create_all)
            
        logger.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {e}")
        raise

async def close_db() -> None:
    """
    Cierra la conexión a la base de datos.
    
    Esta función se ejecuta durante el shutdown de la aplicación
    para cerrar correctamente todas las conexiones.
    """
    global engine
    try:
        logger.info("Cerrando conexión a la base de datos...")
        if engine is not None:
            await engine.dispose()
            engine = None
        logger.info("Conexión cerrada correctamente")
    except Exception as e:
        logger.error(f"Error cerrando la base de datos: {e}")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Genera una sesión de base de datos asíncrona.
    
    Yields:
        AsyncSession: Sesión de base de datos configurada
    """
    Session = sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with Session() as session:
        yield session
