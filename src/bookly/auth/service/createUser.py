from sqlmodel.ext.asyncio.session import AsyncSession

#
from bookly.auth.userDto import UserCreateDTO
from bookly.auth.userRepository import UserRepository
from bookly.errors import UserAlreadyExists
from bookly.config import settings
from bookly.auth.utils import create_url_safe_token
from bookly.mail import mail, create_message


class CreateUserService:
    def __init__(self, user_repository: UserRepository):
        self.userRepository = user_repository

    async def execute(self, user_data: UserCreateDTO, session: AsyncSession):
        email = user_data.email
        user_exists = await self.userRepository.user_exists(email, session)

        if user_exists:
            raise UserAlreadyExists()

        user_data.role = "user"
        new_user = await self.userRepository.create_user(user_data, session)

        # * Prepar y enviar correo de confirmación
        token = create_url_safe_token({"email": email})
        link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"
        html_message = f"""
        <h1>Verify you email</h1>
        <p>Please click this <a href="{link}">link</a> to verify your email.</p>
        """
        message = create_message(
            recipients=[email], subject="Verify your email", body=html_message
        )

        await mail.send_message(message)

        return {
            "message": "Account Created! Check email to verify you account.",
            "user": new_user,
        }
