from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación.

    Carga las variables de entorno desde el archivo .env.

    Attributes:
        DATABASE_URL: URL de conexión a la base de datos
    """

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Instancia global de configuración
settings: Settings = Settings()
