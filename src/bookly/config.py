from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación.

    Carga las variables de entorno desde el archivo .env.

    Attributes:
        DATABASE_URL: URL de conexión a la base de datos
    """

    # Database
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    # REDIS_HOST: str = "localhost"
    # REDIS_PORT: int = 6379
    # Mail
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    # Server configuration
    DOMAIN: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Instancia global de configuración
settings: Settings = Settings()

broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL
broker_connection_retry_on_startup = True

# Nota: El pool de workers se especifica al iniciar el worker, no en la configuración
# En Windows, usa: celery -A bookly.celery_task.c_app worker --pool=solo
# O para concurrencia: celery -A bookly.celery_task.c_app worker --pool=threads