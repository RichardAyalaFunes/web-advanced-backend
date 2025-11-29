from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, List

from .utils import decode_token
from bookly.db.redis import token_in_blocklist
from bookly.db.main import get_session
from .userRepository import UserRepository
from .userModel import User

user_repository = UserRepository()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        """
        Valida el token de acceso del request.

        Args:
            request: Request de FastAPI

        Returns:
            Diccionario con los datos del token decodificado

        Raises:
            HTTPException: Si el token es inválido, expirado o es un refresh token
        """
        creds = await super().__call__(request)

        # Decodificar el token
        token_data = decode_token(creds.credentials)

        # Verificar que el token es válido
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token is invalid or expired.",
                    "resolution": "Please get new token.",
                },
            )

        if await token_in_blocklist(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "This token has been revoked.",
                    "resolution": "Please get new token.",
                },
            )

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please override this method in child classes.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token.",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an refresh token.",
            )


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]
    user = await user_repository.get_user_by_email(user_email, session)
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action."
        )