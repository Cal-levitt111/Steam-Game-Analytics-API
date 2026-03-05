from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core import settings
from app.core.error_handlers import register_exception_handlers
from app.core.transport_security import HTTPSRedirectMiddleware, SecurityHeadersMiddleware
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.collections import router as collections_router
from app.routers.developers import router as developers_router
from app.routers.games import router as games_router
from app.routers.genres import router as genres_router
from app.routers.health import router as health_router
from app.routers.publishers import router as publishers_router
from app.routers.search import router as search_router
from app.routers.tags import router as tags_router

MCP_READONLY_TAGS = [
    'health',
    'games',
    'search',
    'genres',
    'tags',
    'developers',
    'publishers',
    'analytics',
]


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    if settings.allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    app.add_middleware(
        SecurityHeadersMiddleware,
        trusted_proxy_cidrs=tuple(settings.trusted_proxy_cidrs),
        hsts_max_age_seconds=settings.hsts_max_age_seconds,
    )
    app.add_middleware(
        HTTPSRedirectMiddleware,
        force_https=settings.force_https,
        trusted_proxy_cidrs=tuple(settings.trusted_proxy_cidrs),
    )
    register_exception_handlers(app)
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(games_router, prefix=settings.api_prefix)
    app.include_router(search_router, prefix=settings.api_prefix)
    app.include_router(genres_router, prefix=settings.api_prefix)
    app.include_router(tags_router, prefix=settings.api_prefix)
    app.include_router(developers_router, prefix=settings.api_prefix)
    app.include_router(publishers_router, prefix=settings.api_prefix)
    app.include_router(collections_router, prefix=settings.api_prefix)
    app.include_router(analytics_router, prefix=settings.api_prefix)

    if settings.enable_mcp_server:
        mcp = FastApiMCP(
            app,
            name=settings.app_name,
            describe_all_responses=True,
            include_tags=MCP_READONLY_TAGS,
        )
        mcp.mount(mount_path=settings.mcp_mount_path)
        app.state.mcp = mcp

    return app


app = create_app()
