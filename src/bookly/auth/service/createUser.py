from bookly.auth.userDto import UserCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from bookly.auth.userRepository import UserRepository


class CreateUserService:
    def __init__(self, user_repository: UserRepository):
        self.userRepository = user_repository

    async def execute(self, user_data: UserCreateModel, session: AsyncSession):
        email = user_data.email
        user_exists = await self.userRepository.user_exists(email, session)

        if user_exists:
            raise ValueError("User already exists")

        user_data.role = "user"
        new_user = await self.userRepository.create_user(user_data, session)
        return new_user
