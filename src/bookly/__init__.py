
# * Command to run the app: poetry run uvicorn bookly:app --host 0.0.0.0 --port 8000 --reload
"""
Bookly API - Aplicación principal.

Este módulo inicializa la aplicación FastAPI y registra todos los routers.
"""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from bookly.book.BookControllers import book_router
from bookly.book.exceptions import (
    BooklyException,
    bookly_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from contextlib import asynccontextmanager
import logging
from bookly.db.main import init_db, close_db
from bookly.db.redis import init_redis, close_redis
import uvicorn
from bookly.auth.userRouter import auth_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    
    STARTUP: Inicializa recursos antes de que la app reciba requests.
    SHUTDOWN: Limpia recursos cuando la app se detiene.
    
    Args:
        app: Instancia de FastAPI
    """
    # * STARTUP
    logger.info("Iniciando aplicación...")
    
    # Database Connection
    logger.info("DatabaseConnection - Inicializando conexión a base de datos...")
    await init_db()
    logger.info("DatabaseConnection - Conexión a la BD exitosa")
    
    # Redis Connection
    logger.info("RedisConnection - Inicializando conexión a Redis...")
    await init_redis()
    logger.info("RedisConnection - Conexión a Redis exitosa")
    
    # Aplicación lista 
    logger.info("Aplicación lista para recibir requests")
    logger.info("=" * 50)


    yield  # ← La aplicación corre aquí y procesa requests
    
    
    # * SHUTDOWN
    logger.info("=" * 50)
    logger.info(" Deteniendo aplicación...")

    logger.info("Cerrando conexión a base de datos...")
    await close_db()
    
    logger.info("Cerrando conexión a Redis...")
    await close_redis()
    
    logger.info("Recursos liberados correctamente")
    
    logger.info("=" * 50)
    logger.info("Aplicación detenida correctamente")



version: str = "v1"
version_prefix: str = f"/api/{version}"
description: str = "A REST API for a book review web service."


app: FastAPI = FastAPI(
    title="Bookly",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Richard Ayala",
        "url": "https://github.com/RichardAyalaFunes",
        "email": "ayala.funes06@gmail.com",
    }
)

# Registrar manejadores de excepciones personalizados
app.add_exception_handler(BooklyException, bookly_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)