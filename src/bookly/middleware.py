from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

# Códigos ANSI para colores
class Colors:
    """Códigos ANSI para colorear la salida en terminal."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Colores básicos
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    
    # Colores brillantes
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_CYAN = "\033[96m"


def get_method_color(method: str) -> str:
    """
    Retorna el color apropiado para cada método HTTP.
    
    Args:
        method: Método HTTP (GET, POST, PUT, etc.)
        
    Returns:
        Código ANSI de color para el método
    """
    method_colors = {
        "GET": Colors.BRIGHT_GREEN,      # Verde brillante para lectura
        "POST": Colors.BRIGHT_BLUE,      # Azul brillante para creación
        "PUT": Colors.BRIGHT_YELLOW,     # Amarillo brillante para actualización completa
        "PATCH": Colors.YELLOW,          # Amarillo para actualización parcial
        "DELETE": Colors.BRIGHT_RED,     # Rojo brillante para eliminación
        "OPTIONS": Colors.CYAN,          # Cyan para opciones
        "HEAD": Colors.MAGENTA,          # Magenta para HEAD
    }
    return method_colors.get(method.upper(), Colors.RESET)  # Sin color para métodos desconocidos


def get_status_color(status_code: int) -> str:
    """
    Retorna el color apropiado para cada código de estado HTTP.
    
    Args:
        status_code: Código de estado HTTP
        
    Returns:
        Código ANSI de color para el código de estado
    """
    if 200 <= status_code < 300:
        return Colors.BRIGHT_GREEN  # Verde para éxito
    elif 300 <= status_code < 400:
        return Colors.BRIGHT_CYAN   # Cyan para redirecciones
    elif 400 <= status_code < 500:
        return Colors.BRIGHT_YELLOW # Amarillo para errores del cliente
    elif 500 <= status_code < 600:
        return Colors.BRIGHT_RED    # Rojo para errores del servidor
    else:
        return Colors.RESET


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_loggin(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        processing_time = time.time() - start_time
        
        # Obtener colores para método y código de estado
        method_color = get_method_color(request.method)
        status_color = get_status_color(response.status_code)
        
        # Construir mensaje con colores
        method_colored = f"{method_color}{Colors.BOLD}{request.method}{Colors.RESET}"
        status_colored = f"{status_color}{Colors.BOLD}{response.status_code}{Colors.RESET}"
        
        message = (
            f"{request.client.host}:{request.client.port} "
            f"{method_colored} "
            f"{request.url.path} - "
            f"{status_colored} - "
            f"completed in {processing_time:.4f}s"
        )
        print(message)

        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # app.add_middleware(TrustedHostMiddleware, allow_host=["localhost", "127.0.0.1"])

    # Not used for this project ->
    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     if not "Authorization" in request.headers:
    #         return JSONResponse(
    #             content={
    #                 "message": "Not authenticated",
    #                 "resolution": "Please provide the right credential to proceed.",
    #             },
    #             status_code=status.HTTP_401_UNAUTHORIZED
    #         )

    #     response = await call_next(request)
    #     return response
