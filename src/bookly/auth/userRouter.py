from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta

from bookly.auth.userSchemas import UserCreateModel, UserModel, UserLoginModel
from bookly.db.main import get_session
from bookly.auth.userRepository import UserRepository
from bookly.auth.service.createUser import CreateUserService
from fastapi.responses import JSONResponse
from .utils import create_access_token, verify_password

auth_router = APIRouter()

REFRESH_TOKEN_EXPIRY=2

@auth_router.post("/signup", response_model=UserModel)
async def create_user_account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    userRepository = UserRepository()
    createUserService = CreateUserService(userRepository)

    return await createUserService.execute(user_data, session)

@auth_router.post("/login")
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    
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
                    'email': user.email,
                    'user_uid': str(user.uid)
                }
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    "message": "Login sucessful",
                    "access_token": access_token, 
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email, 
                        "uid": str(user.uid)
                    }
                }
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password."
    )