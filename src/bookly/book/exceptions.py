from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional


class BooklyException(HTTPException):
    """
    Excepción personalizada para retornar estructura consistente de errores.
    
    Attributes:
        status_code: Código HTTP de estado
        message: Mensaje general del error
        detail: Detalle específico del error
        error_code: Código de error para el frontend
    """
    def __init__(
        self,
        status_code: int,
        message: str,
        detail: str,
        error_code: str
    ):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail)


async def bookly_exception_handler(request: Request, exc: BooklyException) -> JSONResponse:
    """
    Manejador de excepciones personalizadas de Bookly.
    
    Args:
        request: Objeto Request de FastAPI
        exc: Excepción personalizada BooklyException
        
    Returns:
        JSONResponse con estructura estandarizada de error
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "detail": exc.detail,
            "error_code": exc.error_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Manejador de errores de validación de Pydantic.
    
    Args:
        request: Objeto Request de FastAPI
        exc: Excepción de validación
        
    Returns:
        JSONResponse con estructura estandarizada de error
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Error de validación",
            "detail": str(exc.errors()),
            "error_code": "VALIDATION_ERROR"
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Manejador genérico de excepciones no capturadas.
    
    Args:
        request: Objeto Request de FastAPI
        exc: Excepción genérica
        
    Returns:
        JSONResponse con estructura estandarizada de error
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Error interno del servidor",
            "detail": str(exc),
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

