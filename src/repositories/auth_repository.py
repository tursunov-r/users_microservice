from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.auth_exceptions import InvalidCredentials, Unauthorized
from src.models.user_model import UserModel
from src.schemas.user_schemas import (
    TokenData,
    UserLoginSchema,
)
from src.utils.auth import verify_password


class AuthRepository:
    @staticmethod
    async def login_user_query(user: UserLoginSchema, session: AsyncSession):
        """
        Возвращает пользователя для авторизации,
        только если его email есть в БД и он не заблокирован.
        """
        query = await session.execute(
            select(UserModel).where(
                and_(
                    UserModel.email == str(user.email).lower(),
                    UserModel.is_active.is_(True),
                )
            )
        )
        result = query.scalar_one_or_none()
        if result:
            verified = verify_password(user.password, result.password)
            if verified:
                return result
        raise InvalidCredentials("Invalid credentials")

    @staticmethod
    async def get_profile_query(session: AsyncSession, user: TokenData):
        """Возвращает профиль аутентифицированного пользователя."""
        result = await session.execute(
            select(UserModel).where(
                and_(
                    UserModel.id == user.user_id, UserModel.email == user.email
                )
            )
        )
        user = result.scalar_one_or_none()
        if user:
            return user
        raise Unauthorized("User not authorized")


auth_repository = AuthRepository()
