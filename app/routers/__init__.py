from app.routers.auth import router as auth_router
from app.routers.collections import router as collections_router
from app.routers.developers import router as developers_router
from app.routers.games import router as games_router
from app.routers.genres import router as genres_router
from app.routers.health import router as health_router
from app.routers.publishers import router as publishers_router
from app.routers.search import router as search_router
from app.routers.tags import router as tags_router

__all__ = [
    'auth_router',
    'collections_router',
    'developers_router',
    'games_router',
    'genres_router',
    'health_router',
    'publishers_router',
    'search_router',
    'tags_router',
]