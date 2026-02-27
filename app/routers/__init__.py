from app.routers.auth import router as auth_router
from app.routers.games import router as games_router
from app.routers.genres import router as genres_router
from app.routers.health import router as health_router
from app.routers.search import router as search_router

__all__ = ['auth_router', 'games_router', 'genres_router', 'health_router', 'search_router']