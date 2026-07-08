from datetime import datetime, timedelta

from fastapi import Request
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.settings import settings
from src.exceptions.auth_exceptions import Unauthorized
from src.schemas.user_schemas import TokenData

pwd_context = CryptContext(
    schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto"
)

JWT_SECRET_KEY = settings.jwt_secret
JWT_ACCESS_COOKIE_NAME = settings.JWT_ACCESS_COOKIE_NAME
JWT_TOKEN_LOCATION = settings.JWT_TOKEN_LOCATION
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta):
    """Создать JWT токен"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(hours=1)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: dict, expires_delta: timedelta = timedelta(days=7)
):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """Проверить JWT токен"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(
            user_id=payload.get("user_id"),
            email=payload.get("email"),
            role=payload.get("role"),
        )
    except JWTError:
        return None


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return TokenData(
            user_id=payload.get("user_id"),
            email=payload.get("email"),
            role=payload.get("role"),
        )
    except JWTError:
        return None


async def get_current_user(request: Request):
    token = request.cookies.get(settings.JWT_ACCESS_COOKIE_NAME)

    if not token:
        raise Unauthorized("You are not authorized")

    token_data = verify_token(token)

    if not token_data:
        raise Unauthorized("Invalid token")

    return token_data


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(user_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(user_password, hashed_password)
