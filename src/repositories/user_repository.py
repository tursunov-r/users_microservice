from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import settings
from src.exceptions.auth_exceptions import InvalidCredentials
from src.exceptions.user_exceptions import UserAlreadyExists, UserNotFound
from src.models.user_model import UserModel
from src.schemas.Pagination_schemas import PaginationParams
from src.schemas.admin_schemas import (
    AdminUserCreateSchema,
    AdminUserUpdateSchema,
)
from src.schemas.user_schemas import (
    TokenData,
    UserCreateSchema,
    UserLoginSchema,
    UserUpdateSchema,
)
from src.utils.auth import hash_password, verify_password


class UserRepository:
    @staticmethod
    async def create_user_query(
        user: UserCreateSchema | AdminUserCreateSchema, session: AsyncSession
    ):
        """
        Регистрирует пользователя в БД
        """
        existing = await session.execute(
            select(UserModel).where(UserModel.email == user.email)
        )
        if existing.scalar_one_or_none():
            raise UserAlreadyExists("User already exists")

        hash_pwd = hash_password(user.password)
        query = UserModel(
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            email=str(user.email).lower(),
            password=hash_pwd,
            role="user",  # дефолтная роль
        )

        if isinstance(user, AdminUserCreateSchema):
            query.role = user.role if user.role else "user"

        session.add(query)
        await session.flush()
        return query

    @staticmethod
    async def get_users_query(
        session: AsyncSession, pagination: PaginationParams
    ):
        """Возвращает список пользователей из БД"""
        result = await session.execute(
            select(UserModel).limit(pagination.limit).offset(pagination.offset)
        )
        users = result.scalars().all()
        if users:
            return users
        raise UserNotFound("User not found")

    @staticmethod
    async def get_user_by_id_query(user_id: int, session: AsyncSession):
        """Возвращает данные пользователя по id"""
        user = await session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        result = user.scalar_one_or_none()
        if result:
            return result
        raise UserNotFound("User not found")

    @staticmethod
    async def update_user_query(
        token: TokenData,
        user: UserUpdateSchema | AdminUserUpdateSchema,
        session: AsyncSession,
    ):
        """
        Обновляет пользователя, если пользователь обновляет себя сам,
        он не может изменить свою роль.
        Обновление роли доступно только администратору.
        """
        if isinstance(user, AdminUserUpdateSchema):
            # если запрос на обновление пользователя от админа
            # (user_id из схемы)
            query = await session.execute(
                select(UserModel).where(UserModel.id == user.user_id)
            )
        else:
            # иначе получаем id пользователя из JWT,
            # так как api пользователя не может указывать произвольный user_id
            query = await session.execute(
                select(UserModel).where(UserModel.id == token.user_id)
            )

        result = query.scalar_one_or_none()
        if result:
            if user.first_name:
                result.first_name = user.first_name.title()
            if user.middle_name:
                result.middle_name = user.middle_name.title()
            if user.last_name:
                result.last_name = user.last_name.title()
            if user.password and user.confirm_password:
                result.password = hash_password(user.password)
            if user.email:
                result.email = str(user.email).lower()
            if isinstance(user, AdminUserUpdateSchema):
                # если пользователя обновляет админ, можно обновить роль и восстановить пользователя.
                if user.role:
                    result.role = user.role
                if user.is_active:
                    result.is_active = user.is_active

            session.add(result)
            return result
        raise UserNotFound("User not found")

    @staticmethod
    async def delete_user_query(
        token: TokenData, user: UserLoginSchema, session: AsyncSession
    ):
        """
        Блокировка пользователя по токену (если пользователь этого пожелал сам)
        для подтверждения требуется ввести свой email и пароль.
        """
        query = await session.execute(
            select(UserModel).where(UserModel.id == token.user_id)
        )
        result = query.scalar_one_or_none()
        verify = verify_password(user.password, str(result.password))
        if result.email == user.email and verify:
            result.is_active = False
            session.add(result)
            return result
        raise InvalidCredentials("Invalid credentials, please try again")

    @staticmethod
    async def delete_user_by_id_query(user_id: int, session: AsyncSession):
        """Блокировка пользователя для администратора."""
        query = await session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        result = query.scalar_one_or_none()
        if result:
            result.is_active = False
            session.add(result)
            return result
        raise UserNotFound("User not found")

    @staticmethod
    async def create_admin_query(session: AsyncSession):
        """функция создает администратора как первого пользователя."""
        hash_pwd = hash_password(settings.admin_password)

        result = await session.execute(
            select(UserModel).where(UserModel.email == settings.admin_email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return

        create_admin = UserModel(
            email=settings.admin_email,
            password=hash_pwd,
            first_name=settings.admin_first_name,
            middle_name=settings.admin_middle_name,
            last_name=settings.admin_last_name,
            role="admin",
        )

        session.add(create_admin)


user_repository = UserRepository()
