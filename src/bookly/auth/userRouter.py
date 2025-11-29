from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime

from bookly.auth.userDto import UserCreateModel, UserModel, UserLoginModel, UserBooksModel
from bookly.db.main import get_session
from bookly.auth.userRepository import UserRepository
from bookly.auth.userModel import User
from bookly.auth.service.createUser import CreateUserService
from fastapi.responses import JSONResponse
from .utils import create_access_token, verify_password
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from bookly.db.redis import add_jti_to_blocklist

auth_router = APIRouter()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2  # days


@auth_router.post("/signup", response_model=UserModel)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    userRepository = UserRepository()
    createUserService = CreateUserService(userRepository)

    return await createUserService.execute(user_data, session)


@auth_router.post("/login")
async def login_users(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):

    # Esta lógica debería de estar en un Service
    email = login_data.email
    password = login_data.password

    userRepository = UserRepository()

    user = await userRepository.get_user_by_email(email, session)

    if user is not None and user.password_hash:
        pass_valid = verify_password(password, user.password_hash)

        if pass_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
                expiry=timedelta(hours=1),  # Access token expira en 1 hora
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login sucessful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password."
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired refresh token.",
    )


@auth_router.get("/me", response_model=UserBooksModel)
async def get_me(
    user: User = Depends(get_current_user), _: bool = Depends(role_checker)
) -> UserBooksModel:
    """
    Obtiene la información del usuario actual.
    Requiere autenticación y rol de admin.
    """
    return user


@auth_router.get("/logout")
async def revoke_token(token_detail: dict = Depends(AccessTokenBearer())):
    jti = token_detail["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Loggued out successfully."}, status_code=status.HTTP_200_OK
    )
