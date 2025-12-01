from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime
from .userModel import User
from .userDto import UserCreateDTO
from .utils import generate_passwd_hash


class UserRepository:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User:
        stm = select(User).where(User.email == email)
        result = await session.exec(stm)
        user = result.first()
        return user

    async def user_exists(self, email, session: AsyncSession) -> bool:
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(
        self, user_data: UserCreateDTO, session: AsyncSession
    ) -> User:
        user_dict = user_data.model_dump()
        # Remover password del dict ya que no es un campo del modelo User
        password = user_dict.pop("password")

        new_user = User(**user_dict)
        new_user.password_hash = generate_passwd_hash(password)

        session.add(new_user)
        await session.commit()

        # Refrescar el objeto para obtener los valores generados por la BD (uid, created_at, updated_at)
        await session.refresh(new_user)

        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession) -> User:
        """
        Actualiza los datos de un usuario.

        Args:
            user: Instancia del usuario a actualizar
            user_data: Diccionario con los datos a actualizar
            session: Sesión de base de datos asíncrona

        Returns:
            Usuario actualizado
        """
        # Actualizar todos los campos del diccionario
        for key, value in user_data.items():
            setattr(user, key, value)
        
        # Actualizar la fecha de modificación
        user.updated_at = datetime.now()
        
        # Guardar cambios en la base de datos
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user
