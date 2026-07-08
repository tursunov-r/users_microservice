from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_connect import get_session
from src.core.limiter import limiter
from src.schemas.Pagination_schemas import PaginationParams
from src.schemas.admin_schemas import (
    AdminUserCreateResponseSchema,
    AdminUserCreateSchema,
    AdminUserDataResponseSchema,
    AdminUserUpdateSchema,
)
from src.schemas.user_schemas import TokenData
from src.services.admin_service import admin_service
from src.utils.require_admin import require_admin

router = APIRouter(prefix="/api/v1/admin/users", tags=["admin v1"])


@router.post(
    "/", response_model=AdminUserCreateResponseSchema, status_code=201
)
@limiter.limit("10/minute")
async def create_user(
    user: AdminUserCreateSchema,
    request: Request,
    session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(require_admin),
):
    """Эндпоинт создает пользователя от имени администратора
    и позволяет так же указать роль пользователя"""
    result = await admin_service.create_user(
        user=user, session=session, token=token
    )
    return {"message": "create success", "data": result}


@router.get("/", response_model=list[AdminUserDataResponseSchema])
@limiter.limit("10/minute")
async def get_users(
    request: Request,
    pagination: PaginationParams = Depends(PaginationParams),
    session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(require_admin),
):
    """Возвращает список всех пользователей,
    доступно только пользователям с ролью admin"""
    users = await admin_service.get_users(
        session=session, token=token, pagination=pagination
    )
    return users


@router.get("/{user_id}")
@limiter.limit("10/minute")
async def get_user_by_id(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(require_admin),
):
    """Возвращает данные о пользователе по id,
    доступно только пользователям с ролью admin"""
    result = await admin_service.get_user_by_id(
        user_id=user_id, session=session, token=token
    )
    return result


@router.patch("/", response_model=AdminUserCreateResponseSchema)
@limiter.limit("10/minute")
async def update_user(
    user: AdminUserUpdateSchema,
    request: Request,
    session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(require_admin),
):
    """Обновляет пользователя, можно изменить и роль и пароль,
    доступно только admin"""
    updated_user = await admin_service.update_user(
        user=user, session=session, token=token
    )
    return {"message": "update success", "data": updated_user}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("1/minute")
async def delete_user(
    user_id: int,
    request: Request,
    token: TokenData = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Блокирует пользователя по id доступно только admin"""
    await admin_service.delete_user(
        user_id=user_id, session=session, token=token
    )
    return status.HTTP_204_NO_CONTENT
