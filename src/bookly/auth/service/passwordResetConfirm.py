from sqlmodel.ext.asyncio.session import AsyncSession

from bookly.auth.userDto import PasswordResetConfirmModel
from bookly.auth.userRepository import UserRepository
from bookly.auth.utils import decode_url_safe_token, generate_passwd_hash
from bookly.errors import InvalidToken, UserNotFound, ValidationError


class PasswordResetConfirmService:
    """
    Servicio para confirmar el restablecimiento de contraseña.
    
    Sigue el patrón de Clean Architecture separando la lógica de negocio
    de la capa de presentación (controller).
    """
    
    def __init__(self, user_repository: UserRepository):
        self.userRepository = user_repository

    async def execute(
        self, token: str, passwords: PasswordResetConfirmModel, session: AsyncSession
    ) -> dict:
        """
        Ejecuta la confirmación del restablecimiento de contraseña.
        
        Args:
            token: Token de verificación obtenido del email
            passwords: DTO con la nueva contraseña y confirmación
            session: Sesión de base de datos asíncrona
            
        Returns:
            Diccionario con mensaje de éxito
            
        Raises:
            ValidationError: Si las contraseñas no coinciden
            InvalidToken: Si el token es inválido
            UserNotFound: Si el usuario no existe
        """
        # Validar que las contraseñas coincidan
        if passwords.confirm_password != passwords.new_password:
            raise ValidationError("Passwords don't match.")

        # Decodificar el token para obtener el email
        token_data = decode_url_safe_token(token)
        if not token_data:
            raise InvalidToken()
        
        user_email = token_data.get("email")
        if not user_email:
            raise InvalidToken()

        # Buscar el usuario por email
        user = await self.userRepository.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        # Generar hash de la nueva contraseña y actualizar
        pass_hash = generate_passwd_hash(passwords.new_password)
        await self.userRepository.update_user(
            user, {"password_hash": pass_hash}, session
        )

        return {
            "message": "Password reset successfully"
        }
