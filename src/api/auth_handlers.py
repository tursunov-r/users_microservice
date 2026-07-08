from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.db_connect import get_session
from src.core.limiter import limiter
from src.schemas.user_schemas import UserLoginSchema
from src.services.profile_service import profile_service

router = APIRouter(prefix="/api/v1/profiles", tags=["profile v1"])


@router.post("/")
@limiter.limit("5/minute")
async def login(
    user: UserLoginSchema,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Аутентификация пользователя"""
    result = await profile_service.login_user(
        user=user, response=response, session=session
    )
    return result


@router.delete("/")
@limiter.limit("5/minute")
async def logout(
    request: Request,
    response: Response,
):
    """Выйти из системы"""
    await profile_service.logout_user(response)

    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/refresh")
@limiter.limit("5/minute")
async def refresh_tokens(
    request: Request,
    response: Response,
):
    """Refresh token для обновления access token
    Если нет refresh token вызывается исключений Unauthorized"""
    refresh = await profile_service.refresh_user(
        request=request, response=response
    )
    return refresh
