from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.user_repository import user_repository
from src.schemas.Pagination_schemas import PaginationParams
from src.schemas.admin_schemas import (
    AdminUserCreateSchema,
    AdminUserUpdateSchema,
)
from src.schemas.user_schemas import TokenData
from src.services.logger import log_service


class AdminService:
    @staticmethod
    async def create_user(
        user: AdminUserCreateSchema, token: TokenData, session: AsyncSession
    ):
        result = await user_repository.create_user_query(
            user=user, session=session
        )
        log_service.info(f"{token.email} created user:", user=user.email)
        return result

    @staticmethod
    async def get_users(
        session: AsyncSession, token: TokenData, pagination: PaginationParams
    ):
        result = await user_repository.get_users_query(
            session=session, pagination=pagination
        )
        log_service.info(
            f"{token.email} retrieved users: ", users_count=len(result)
        )
        return result

    @staticmethod
    async def get_user_by_id(
        user_id: int, session: AsyncSession, token: TokenData
    ):
        result = await user_repository.get_user_by_id_query(
            user_id=user_id, session=session
        )
        log_service.info(f"{token.email} retrieved user: ", user=user_id)
        return result

    @staticmethod
    async def update_user(
        user: AdminUserUpdateSchema, token: TokenData, session: AsyncSession
    ):
        result = await user_repository.update_user_query(
            token=token, user=user, session=session
        )
        log_service.info(f"{token.email} updated user: ", user=user.user_id)
        return result

    @staticmethod
    async def delete_user(
        user_id: int, session: AsyncSession, token: TokenData
    ):
        result = await user_repository.delete_user_by_id_query(
            user_id=user_id, session=session
        )
        log_service.info(f"{token.email} deleted user: ", user=user_id)
        return result


admin_service = AdminService()
