# Endpoint Matrix And Coursework Coverage

## Endpoint Matrix

All routes below are implemented in the running application. The `Auth` column reflects production behavior. In `ENVIRONMENT=development`, Swagger/OpenAPI and read-only routes are left open for local testing.

| Resource Group | Endpoints | Auth |
|---|---|---|
| Auth | `POST /api/v1/auth/register`, `POST /api/v1/auth/login` | No |
| Auth | `GET /api/v1/auth/me`, `PUT /api/v1/auth/me` | Yes |
| Health | `GET /api/v1/health` | Yes |
| JWKS | `GET /.well-known/jwks.json` | Yes |
| Games | `GET /api/v1/games`, `GET /api/v1/games/{id}`, `GET /api/v1/games/{id}/similar` | Yes |
| Search | `GET /api/v1/search` | Yes |
| Genres | `GET /api/v1/genres`, `GET /api/v1/genres/{slug}`, `GET /api/v1/genres/{slug}/games` | Yes |
| Tags | `GET /api/v1/tags`, `GET /api/v1/tags/{slug}`, `GET /api/v1/tags/{slug}/games` | Yes |
| Developers | `GET /api/v1/developers`, `GET /api/v1/developers/{slug}`, `GET /api/v1/developers/{slug}/games` | Yes |
| Publishers | `GET /api/v1/publishers`, `GET /api/v1/publishers/{slug}`, `GET /api/v1/publishers/{slug}/games` | Yes |
| Collections | `POST /api/v1/collections`, `GET /api/v1/collections`, `GET /api/v1/collections/public`, `GET /api/v1/collections/{id}`, `PUT /api/v1/collections/{id}`, `DELETE /api/v1/collections/{id}`, `POST /api/v1/collections/{id}/games/{game_id}`, `DELETE /api/v1/collections/{id}/games/{game_id}` | Yes |
| Analytics | `GET /api/v1/analytics/release-trends`, `GET /api/v1/analytics/top-genres`, `GET /api/v1/analytics/genre-growth`, `GET /api/v1/analytics/price-distribution`, `GET /api/v1/analytics/top-developers`, `GET /api/v1/analytics/score-by-genre`, `GET /api/v1/analytics/free-vs-paid`, `GET /api/v1/analytics/platform-breakdown`, `GET /api/v1/analytics/review-sentiment` | Yes |
| MCP | `GET /mcp`, `POST /mcp/messages/` | Yes when `ENABLE_MCP_SERVER=true` |

Total implemented endpoints: 41

Runtime OpenAPI/Swagger endpoints are available in development and disabled in production. Generate and host API docs separately from the OpenAPI schema if required for submission or deployment.

## Coursework Criteria Mapping

| Criterion | Implemented Evidence |
|---|---|
| CRUD operations | Full CRUD for collections plus collection membership add/remove |
| 4+ endpoints | 41 implemented endpoints across auth, catalogue, search, taxonomy, collections, analytics, health, JWKS, and MCP |
| SQL database usage | PostgreSQL schema in 3NF with dimension tables, junction tables, collections, and migrations |
| JSON + status codes | Standard JSON responses and standardised error envelope across handled errors |
| Authentication | JWT bearer auth with RS256 signing, rate limiting, ownership checks, and protected application surface |
| API documentation | OpenAPI schema can be generated locally and linked externally; runtime docs are available in development and disabled in production |
| Testing | Pytest suite for auth, collections, analytics, taxonomy, similarity, migrations, transport security, MCP, and error handling |
| Architecture quality | Layered router -> service -> repository structure plus typed schemas and migrations |
| Advanced querying | PostgreSQL full-text search, pgvector similarity, pagination/filtering, and aggregate analytics |
| Advanced integration | Optional MCP server with read-only allowlist and auth-gated transport endpoints |

## Verification Commands

```powershell
python -m pytest -q
python -m alembic upgrade head --sql > nul
python scripts/import_games.py --mode seed --dry-run
python scripts/generate_embeddings.py --mode seed --only-missing
```
