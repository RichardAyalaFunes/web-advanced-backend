from sqlmodel.ext.asyncio.session import AsyncSession

from bookly.auth.userDto import PasswordResetRequestDTO
from bookly.auth.userRepository import UserRepository
from bookly.errors import UserNotFound
from bookly.config import settings
from bookly.auth.utils import create_url_safe_token
from bookly.mail import mail, create_message


class PasswordResetRequestService:
    """
    Servicio para solicitar el restablecimiento de contraseña.
    
    Sigue el patrón de Clean Architecture separando la lógica de negocio
    de la capa de presentación (controller).
    """
    
    def __init__(self, user_repository: UserRepository):
        self.userRepository = user_repository

    async def execute(self, email_data: PasswordResetRequestDTO, session: AsyncSession) -> dict:
        """
        Ejecuta la solicitud de restablecimiento de contraseña.
        
        Args:
            email_data: DTO con el email del usuario
            session: Sesión de base de datos asíncrona
            
        Returns:
            Diccionario con mensaje de éxito
            
        Raises:
            UserNotFound: Si el usuario no existe
        """
        email = email_data.email
        
        # Verificar que el usuario existe
        user = await self.userRepository.get_user_by_email(email, session)
        if not user:
            raise UserNotFound()
        
        # Preparar y enviar correo de confirmación
        token = create_url_safe_token({"email": email})
        link = f"http://{settings.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
        html_message = f"""
        <h1>Reset your password.</h1>
        <p>Please click this <a href="{link}">link</a> to reset your password.</p>
        """
        message = create_message(
            recipients=[email],
            subject="Reset your password - FastAPI",
            body=html_message,
        )

        await mail.send_message(message)

        return {
            "message": "Please check your email for instructions to reset your password."
        }
