from sqlmodel.ext.asyncio.session import AsyncSession

from bookly.auth.userRepository import UserRepository
from bookly.auth.utils import decode_url_safe_token
from bookly.errors import UserNotFound


class ValidateUserService:
    """
    Servicio para validar/verificar la cuenta de usuario mediante token.

    Sigue el patrón de Clean Architecture separando la lógica de negocio
    de la capa de presentación (controller).
    """

    def __init__(self, user_repository: UserRepository):
        self.userRepository = user_repository

    async def execute(self, token: str, session: AsyncSession) -> dict:
        """
        Ejecuta la validación del usuario mediante token.

        Args:
            token: Token de verificación obtenido del email
            session: Sesión de base de datos asíncrona

        Returns:
            Diccionario con mensaje de éxito

        Raises:
            UserNotFound: Si el usuario no existe o el token es inválido
        """
        # Decodificar el token para obtener el email
        token_data = decode_url_safe_token(token)
        if not token_data:
            raise UserNotFound()

        user_email = token_data.get("email")
        if not user_email:
            raise UserNotFound()

        # Buscar el usuario por email
        user = await self.userRepository.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        # Actualizar el estado de verificación del usuario usando el repositorio
        verified_user = await self.userRepository.update_user(
            user, {"is_verified": True}, session
        )

        return {
            "message": "Account verified successfully!",
            "user": verified_user,
        }
