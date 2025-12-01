from datetime import timedelta, datetime
from itsdangerous import URLSafeTimedSerializer
import bcrypt
import jwt
import uuid
import logging

#
from bookly.config import settings

ACCESS_TOKE_EXPIRY = 3600

# 
# * Password management
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

    # Generar salt y hash usando bcrypt directamente
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hash_bytes.decode("utf-8")


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
        # Verificar contraseña usando bcrypt directamente
        hash_bytes = hash.encode("utf-8")
        password_bytes = password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except (ValueError, TypeError, Exception) as e:
        logging.error(
            f"verify_password: error verifying password - {type(e).__name__}: {e}"
        )
        return False

# 
# * Token Management
def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    """
    Crea un token JWT de acceso o refresh.

    Args:
        user_data: Diccionario con los datos del usuario
        expiry: Tiempo de expiración del token (por defecto 1 hora)
        refresh: Si es True, crea un refresh token; si es False, crea un access token

    Returns:
        Token JWT como string
    """
    payload = {}

    payload["user"] = user_data
    # JWT exp debe ser un timestamp Unix (int), no un datetime
    expiry_time = (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKE_EXPIRY)
    )
    payload["exp"] = int((datetime.now() + expiry_time).timestamp())
    payload["iat"] = int(datetime.now().timestamp())  # Issued at
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    # jwt.encode siempre devuelve un string en PyJWT 2.x
    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token  # Siempre es un string


def decode_token(token: str) -> dict | None:
    """
    Decodifica y verifica un token JWT.

    Args:
        token: Token JWT como string (siempre viene del header HTTP como string)

    Returns:
        Diccionario con los datos del token si es válido, None en caso contrario
    """
    try:
        token_data = jwt.decode(
            token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None

# 
# * URL tokens
serializer = URLSafeTimedSerializer(
    secret_key=settings.JWT_SECRET, salt="email-configuration"
)

def create_url_safe_token(data: dict):
    return serializer.dumps(data, salt="email-configuration")

def decode_url_safe_token(token: str):
    try: 
        return serializer.loads(token)
    
    except Exception as e:
        logging.error(str(e))



