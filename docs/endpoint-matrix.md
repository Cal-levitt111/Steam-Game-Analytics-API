# Endpoint Matrix And Coursework Coverage

## Endpoint Matrix

| Resource Group | Endpoints |
|---|---|
| Auth | `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `PUT /api/v1/auth/me` |
| Games | `GET /api/v1/games`, `GET /api/v1/games/{id}`, `GET /api/v1/games/{id}/similar` |
| Search | `GET /api/v1/search` |
| Genres | `GET /api/v1/genres`, `GET /api/v1/genres/{slug}`, `GET /api/v1/genres/{slug}/games` |
| Tags | `GET /api/v1/tags`, `GET /api/v1/tags/{slug}`, `GET /api/v1/tags/{slug}/games` |
| Developers | `GET /api/v1/developers`, `GET /api/v1/developers/{slug}`, `GET /api/v1/developers/{slug}/games` |
| Publishers | `GET /api/v1/publishers`, `GET /api/v1/publishers/{slug}`, `GET /api/v1/publishers/{slug}/games` |
| Collections | `POST /api/v1/collections`, `GET /api/v1/collections`, `GET /api/v1/collections/{id}`, `PUT /api/v1/collections/{id}`, `DELETE /api/v1/collections/{id}`, `POST /api/v1/collections/{id}/games/{game_id}`, `DELETE /api/v1/collections/{id}/games/{game_id}`, `GET /api/v1/collections/public` |
| Analytics | `GET /api/v1/analytics/release-trends`, `GET /api/v1/analytics/top-genres`, `GET /api/v1/analytics/genre-growth`, `GET /api/v1/analytics/price-distribution`, `GET /api/v1/analytics/top-developers`, `GET /api/v1/analytics/score-by-genre`, `GET /api/v1/analytics/free-vs-paid`, `GET /api/v1/analytics/platform-breakdown`, `GET /api/v1/analytics/review-sentiment` |

Total implemented endpoints: 38

## Coursework Criteria Mapping

| Criterion | Implemented Evidence |
|---|---|
| CRUD operations | Full CRUD on collections + membership add/remove |
| 4+ endpoints | 38 endpoints across 9 resource groups |
| SQL database usage | PostgreSQL schema with normalized dimensions + junction tables |
| JSON + status codes | Consistent response/error envelopes and explicit status handling |
| Authentication | JWT bearer auth, protected routes, ownership checks |
| API documentation | FastAPI OpenAPI docs at `/docs` |
| Testing | Pytest suite covering migrations, auth, taxonomy, collections, analytics, API errors |
| Architecture quality | Router -> service -> repository separation with models/schemas |
| Advanced querying | Full-text search + pgvector similarity + aggregation-heavy analytics endpoints |

## Verification Commands

```bash
python -m pytest -q
python -m alembic upgrade head --sql > nul
python scripts/generate_embeddings.py --mode seed --only-missing
```
