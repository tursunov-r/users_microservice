from datetime import timedelta

from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.settings import settings
from src.repositories.auth_repository import auth_repository
from src.schemas.user_schemas import TokenData, UserLoginSchema
from src.services.logger import log_service
from src.utils.auth import create_access_token, create_refresh_token


class ProfileService:
    @staticmethod
    async def login_user(
        user: UserLoginSchema, response: Response, session: AsyncSession
    ):
        login = await auth_repository.login_user_query(
            user=user, session=session
        )
        if not login:
            raise
        # Создание токена
        access_token = create_access_token(
            data={
                "user_id": login.id,
                "email": login.email,
                "role": login.role,
            },
            expires_delta=timedelta(),
        )
        refresh_token = create_refresh_token(
            data={
                "user_id": login.id,
                "email": login.email,
                "role": login.role,
            }
        )

        response.set_cookie(
            key=settings.JWT_ACCESS_COOKIE_NAME,
            value=access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=1 * 24,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 3600,
        )
        log_service.info("logged in user: ", user=user.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def get_user_profile(user: TokenData, session: AsyncSession):
        result = await auth_repository.get_profile_query(
            user=user, session=session
        )
        log_service.info("check self profile: ", user=user.email)
        return result

    @staticmethod
    async def logout_user(response: Response):
        response.delete_cookie(
            key=settings.JWT_ACCESS_COOKIE_NAME,
            httponly=True,
            secure=False,
            samesite="Lax",
        )


profile_service = ProfileService()
