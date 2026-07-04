from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware

from src.api import routers
from src.api.exceprion_handlers import register_exception_handlers
from src.core.database import (
    create_admin,
    create_tables,
    create_test_admin,
    create_test_tables,
)
from src.core.db_connect import get_session, test_get_session
from src.core.limiter import limiter
from src.core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.test:
        await create_tables()
        await create_admin()
    else:
        await create_test_tables()
        await create_test_admin()
    yield


app = FastAPI(lifespan=lifespan)

if settings.test:
    app.dependency_overrides[get_session] = test_get_session

register_exception_handlers(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

for router in routers:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
