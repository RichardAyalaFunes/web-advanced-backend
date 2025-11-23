from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
import uuid
import logging
from bookly.config import settings

passwrd_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKE_EXPIRY = 3600


def generate_passwd_hash(password: str) -> str:
    """
    Genera un hash bcrypt de una contraseña.

    Args:
        password: Contraseña en texto plano a hashear

    Returns:
        Hash bcrypt de la contraseña

    Raises:
        ValueError: Si la contraseña es None o vacía
    """
    if not password:
        raise ValueError("Password cannot be None or empty")

    # Bcrypt tiene un límite de 72 bytes para contraseñas
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        logging.warning(
            f"generate_passwd_hash: password exceeds 72 bytes ({len(password_bytes)}), truncating"
        )
        password = password_bytes[:72].decode("utf-8", errors="ignore")

    hash = passwrd_context.hash(password)
    return hash


def verify_password(password: str, hash: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.

    Args:
        password: Contraseña en texto plano a verificar
        hash: Hash almacenado de la contraseña

    Returns:
        True si la contraseña coincide, False en caso contrario
    """
    if not hash:
        logging.error("verify_password: hash is None or empty")
        return False

    if not password:
        logging.error("verify_password: password is None or empty")
        return False

    # Bcrypt tiene un límite de 72 bytes para contraseñas
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        logging.warning(
            f"verify_password: password exceeds 72 bytes ({len(password_bytes)}), truncating"
        )
        password = password_bytes[:72].decode("utf-8", errors="ignore")

    try:
        return passwrd_context.verify(password, hash)
    except (ValueError, TypeError, Exception) as e:
        logging.error(
            f"verify_password: error verifying password - {type(e).__name__}: {e}"
        )
        return False


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKE_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
