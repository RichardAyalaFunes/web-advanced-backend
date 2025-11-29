"""
Módulo para gestionar la lista de tokens revocados (blocklist) usando Redis.
"""
from redis.asyncio import Redis
from redis.asyncio import from_url
from bookly.config import settings
import logging

logger = logging.getLogger(__name__)

JTI_EXPIRY = 3600  # Tiempo de expiración en Redis (1 hora, igual que el access token)

# Cliente Redis global (se inicializa en init_redis)
token_blocklist: Redis = None


async def init_redis() -> None:
    """
    Inicializa la conexión a Redis.
    Debe ser llamado durante el startup de la aplicación.
    """
    global token_blocklist
    token_blocklist = from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        db=0,
        decode_responses=True
    )
    logger.info(f"Redis conectado en {settings.REDIS_HOST}:{settings.REDIS_PORT}")


async def close_redis() -> None:
    """
    Cierra la conexión a Redis.
    Debe ser llamado durante el shutdown de la aplicación.
    """
    global token_blocklist
    if token_blocklist:
        await token_blocklist.close()
        logger.info("Conexión a Redis cerrada")


async def add_jti_to_blocklist(jti: str) -> None:
    """
    Añade un JTI (JWT ID) a la blocklist de tokens revocados.
    
    Args:
        jti: Identificador único del token JWT a revocar
    """
    if token_blocklist is None:
        await init_redis()
    
    try:
        await token_blocklist.set(name=jti, value="revoked", ex=JTI_EXPIRY)
        logger.info(f"Token JTI {jti} añadido a la blocklist")
    except Exception as e:
        logger.error(f"Error al añadir JTI a blocklist: {e}")
        raise


async def token_in_blocklist(jti: str) -> bool:
    """
    Verifica si un JTI está en la blocklist de tokens revocados.
    
    Args:
        jti: Identificador único del token JWT a verificar
        
    Returns:
        True si el token está revocado, False si es válido
    """
    if token_blocklist is None:
        await init_redis()
    
    try:
        exists = await token_blocklist.exists(jti)
        return exists == 1
    except Exception as e:
        logger.error(f"Error al verificar JTI en blocklist: {e}")
        # En caso de error, permitimos el token (fail-open para evitar bloqueos)
        return False
