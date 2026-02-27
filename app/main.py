from fastapi import FastAPI

from app.core import settings
from app.core.error_handlers import register_exception_handlers
from app.routers.auth import router as auth_router
from app.routers.games import router as games_router
from app.routers.health import router as health_router
from app.routers.search import router as search_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    register_exception_handlers(app)
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(games_router, prefix=settings.api_prefix)
    app.include_router(search_router, prefix=settings.api_prefix)
    return app


app = create_app()