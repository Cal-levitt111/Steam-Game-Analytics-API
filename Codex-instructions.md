# Codex Instructions

## Project Overview
Steam-Game-Analytics-API is a FastAPI backend for browsing and analyzing Steam game data.

Core capabilities implemented so far:
- Authentication with JWT bearer tokens (`register`, `login`, `me`, `update me`).
- Game catalog listing and detail.
- Similar-game recommendations (`/games/{id}/similar`) using pgvector cosine similarity.
- Full-text search over game metadata.
- Taxonomy resources (`genres`, `tags`, `developers`, `publishers`) with list/detail/games views.
- User collections CRUD + membership operations.
- Analytics endpoints for trends, distribution, and aggregate breakdowns.
- Seed/full CSV import pipeline into Postgres.
- Embedding generation pipeline (`scripts/generate_embeddings.py`) for local similarity setup.
- MCP server compatibility mounted at `/mcp` with read-only tool exposure.

API base path: `/api/v1`

## Tech Stack
- Python 3.12
- FastAPI + Starlette
- SQLAlchemy ORM (2.x)
- PostgreSQL (Docker Compose for local DB)
- pgvector extension (vector storage and ANN index)
- fastapi-mcp (MCP server mount from OpenAPI)
- Alembic migrations
- Pydantic v2 for request/response validation
- `python-jose` for JWT
- Pandas for CSV ingestion
- sentence-transformers (`all-MiniLM-L6-v2`) for local embeddings
- Psycopg 3 for DB driver and import writes
- Pytest for tests

Key infra files:
- `docker-compose.yml`
- `.env.example`
- `alembic.ini`
- `app/main.py`

## Repository Layout
- `app/main.py`: FastAPI app factory and router registration.
- `app/core/`: config, DB session dependency, auth dependencies, security helpers, pagination helper, error handlers.
- `app/models/`: SQLAlchemy models and association tables.
- `app/schemas/`: Pydantic request/response models.
- `app/repositories/`: data access layer (SQL queries/ORM operations).
- `app/services/`: business logic layer.
- `app/routers/`: HTTP route definitions.
- `alembic/versions/`: migration history.
- `scripts/import_games.py`: CSV import pipeline.
- `scripts/generate_embeddings.py`: one-off/local embedding generation.
- `scripts/generate_seed_from_dataset.py`: seed extraction helper.
- `tests/`: API/service/migration smoke tests.
- `docs/`: architecture and endpoint matrix documents.

## How Requests Flow
Typical request path:
1. Router receives request and validates path/query/body.
2. Dependencies provide DB session and optional/required user context.
3. Service layer enforces domain rules and raises typed `AppException` for expected failures.
4. Repository layer executes queries.
5. Router serializes response using schemas or plain dict envelopes.

Error handling:
- `app/core/error_handlers.py` centralizes exception handling.
- All errors are normalized to envelope:
  - `{"error":{"code":"...","message":"...","detail":...}}`

## Configuration and Environment
Settings are loaded from `.env` via `pydantic-settings`.

Expected variables:
- `DATABASE_URL` (default local postgres URL)
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ENVIRONMENT`
- `ENABLE_VECTOR_SIMILARITY`
- `EMBEDDING_MODEL`
- `EMBEDDING_DIM`
- `EMBEDDING_BATCH_SIZE`
- `ENABLE_MCP_SERVER`
- `MCP_MOUNT_PATH`

Important note:
- Current defaults are development-friendly, not production-safe (`SECRET_KEY` placeholder and 24h tokens in example).

## Database and Migrations
### Current migration chain
- `9a2f56a2eda1`: base normalized schema.
- `59a9fbcd1491`: search vector + trigger + indexes.
- `4dd6c697e688`: extended game metadata columns.
- `6c2ec617561e`: remove redundant `short_description` and `detailed_description`; move FTS trigger to `about_the_game`.
- `b8f4f9515b2e`: restore search/filter indexes dropped in an earlier revision.
- `c51ef0df6f74`: add pgvector extension usage and `games.embedding` with IVFFlat cosine index.

### Core tables
- `games`
- `genres`, `tags`, `developers`, `publishers`, `categories`
- Junctions: `game_genres`, `game_tags`, `game_developers`, `game_publishers`, `game_categories`
- `users`, `collections`, `collection_games`

### Game data model highlights
Game now stores canonical description in:
- `about_the_game`

Extended metadata includes:
- ownership, ccu, discount, dlc count
- languages, reviews, support links/emails
- metacritic url/user score/score rank
- achievements/recommendations/notes
- playtime metrics
- screenshots/movies
- embedding (`VECTOR(384)`) used by similar-games endpoint

FTS behavior:
- `search_vector` is maintained by trigger using weighted `name`, `about_the_game`, and tag text.

## Auth and Security Model
Implemented:
- Password hashing: PBKDF2-SHA256 + salt.
- JWT access token creation/verification (`HS256`).
- Expiry enforced (`exp` claim).
- `HTTPBearer` auth dependency for protected routes.
- Distinct error codes for invalid/expired/missing auth.

Not yet implemented (advanced hardening):
- Refresh token rotation and token revocation store.
- Rate limiting / lockout.
- HTTPS/HSTS enforcement in app layer.

## Import Pipeline (`scripts/import_games.py`)
Importer supports both normalized and Kaggle-style CSV headers.

### Input modes
- `--mode seed`: uses first available seed CSV from `data/seed` candidates.
- `--mode full --input <path>`: full file import.
- `--dry-run`: parse/normalize only, no writes.

### What importer does
1. Reads CSV.
2. Normalizes column names (`AppID` -> `steam_app_id`, etc.).
3. Normalizes list fields for taxonomy splits (comma/pipe/list-text).
4. Builds canonical game rows.
5. Upserts dimensions with slug collision handling.
6. Upserts games by `steam_app_id` (idempotent conflict updates).
7. Upserts junction rows with `ON CONFLICT DO NOTHING`.
8. Refreshes `search_vector` post-import.

Idempotency:
- Re-running import should not duplicate rows.

## Embedding Pipeline (`scripts/generate_embeddings.py`)
Purpose:
- Generate vector embeddings for game rows and store them in `games.embedding`.

Typical run:
- `python scripts/generate_embeddings.py --mode seed --only-missing`

Useful flags:
- `--limit` (process subset for quick iteration)
- `--batch-size`
- `--only-missing`
- `--dry-run`

## API Endpoints
All routes are under `/api/v1`.

### Health
- `GET /health`
- Returns: `{"status":"ok"}`

### Auth
- `POST /auth/register`
  - Body: `email`, `password (8-128)`, optional `display_name`
  - Returns: user object (`201`)
- `POST /auth/login`
  - Body: `email`, `password`
  - Returns: `{"access_token":"...","token_type":"bearer"}`
- `GET /auth/me` (auth required)
  - Returns current user
- `PUT /auth/me` (auth required)
  - Body: optional `display_name`, optional `password`
  - Returns updated user

### Games
- `GET /games`
  - Supports filters: genre/tag/developer/publisher/platform/is_free/price/score/date range
  - Supports sort and order
  - Returns paginated envelope
- `GET /games/{game_id}`
  - Returns `GameDetail` object (not wrapped in `data`)
- `GET /games/{game_id}/similar`
  - Query: `limit` (default `10`, max `50`)
  - Returns `{"data": [GameListItem + similarity]}`
  - Error paths: `404 RESOURCE_NOT_FOUND`, `409 EMBEDDING_NOT_AVAILABLE`, `501 FEATURE_UNAVAILABLE`

### MCP
- Mount path: `/mcp`
- Implementation: `fastapi-mcp` wraps selected FastAPI operations as tools.
- Exposed tags: `health`, `games`, `search`, `genres`, `tags`, `developers`, `publishers`, `analytics`.
- Excluded from MCP exposure: `auth` and `collections`.

### Search
- `GET /search?q=<query>`
  - `q` required
  - Supports optional `genre`, `tag`, `is_free`, `min_score`
  - Returns paginated list with optional `rank`

### Taxonomy
Genres:
- `GET /genres`
- `GET /genres/{slug}`
- `GET /genres/{slug}/games`

Tags:
- `GET /tags`
- `GET /tags/{slug}`
- `GET /tags/{slug}/games`

Developers:
- `GET /developers`
- `GET /developers/{slug}`
- `GET /developers/{slug}/games`

Publishers:
- `GET /publishers`
- `GET /publishers/{slug}`
- `GET /publishers/{slug}/games`

List endpoints return pagination envelope. Detail endpoints generally return `{"data": ...}` except `/games/{id}`.

### Collections
- `POST /collections` (auth)
- `GET /collections` (auth; current user)
- `GET /collections/public`
- `GET /collections/{collection_id}` (owner or public)
- `PUT /collections/{collection_id}` (owner)
- `DELETE /collections/{collection_id}` (owner)
- `POST /collections/{collection_id}/games/{game_id}` (owner)
- `DELETE /collections/{collection_id}/games/{game_id}` (owner)

### Analytics
- `GET /analytics/release-trends`
- `GET /analytics/top-genres`
- `GET /analytics/genre-growth` (`from`/`to` are integer years)
- `GET /analytics/price-distribution`
- `GET /analytics/top-developers`
- `GET /analytics/score-by-genre`
- `GET /analytics/free-vs-paid`
- `GET /analytics/platform-breakdown`
- `GET /analytics/review-sentiment`

Analytics response shape:
- `{"data": [...], "generated_at": "...", "query_params": {...}}`

## Response Conventions
### Error envelope
All handled errors are standardized:
- `error.code`
- `error.message`
- `error.detail`

Common codes include:
- `VALIDATION_ERROR`, `BAD_REQUEST`, `RESOURCE_NOT_FOUND`, `UNAUTHORIZED`, `TOKEN_INVALID`, `TOKEN_EXPIRED`, `FORBIDDEN`, `CONFLICT`, `EMBEDDING_NOT_AVAILABLE`, `FEATURE_UNAVAILABLE`, `INTERNAL_SERVER_ERROR`.

### Pagination envelope
List routes include:
- `page`, `per_page`, `total`, `total_pages`, `next`, `prev`

## Local Development Workflow
### Boot local stack
1. `python -m venv venv`
2. `venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. `Copy-Item .env.example .env`
5. `docker compose up -d db`
6. `python -m alembic upgrade head`
7. `python scripts/import_games.py --mode seed`
8. `python scripts/generate_embeddings.py --mode seed --only-missing`
9. `uvicorn app.main:app --reload`

Docs UI:
- `http://localhost:8000/docs`

## Testing Strategy
Run full suite:
- `python -m pytest -q`

Current test files:
- `test_auth.py`: auth lifecycle and error paths.
- `test_api_errors.py`: envelope consistency for key failures.
- `test_collections.py`: ownership, conflicts, membership.
- `test_taxonomy.py`: slug resources and counts.
- `test_analytics.py`: analytics response shape/sanity.
- `test_migrations.py`: migration SQL smoke check.
- `test_game_similarity.py`: similar endpoint shape and error handling.
- `test_mcp.py`: MCP mount and read-only exposure boundary checks.

## Known Caveats and Follow-ups
- Security posture is baseline/dev-friendly; production hardening is pending.
- API response wrapping is intentionally mixed in a few places (`/games/{id}` and auth endpoints return plain typed models).
- README references an older seed filename in places; importer logic now auto-resolves available seed CSVs.
- First embedding generation downloads the model from Hugging Face and can take time depending on network.
- On some Windows Docker setups, Postgres may print collation-version warnings after image changes; recreating the DB volume is the simplest local fix.

## Practical Guidance for New Contributors
- Start by reading:
  - `app/main.py`
  - `app/core/*`
  - one vertical slice (`routers/search.py` -> `services/search_service.py` -> `repositories/game_repo.py`).
- Keep business rules in services and SQL/query mechanics in repositories.
- For schema changes:
  1. update models
  2. `python -m alembic revision --autogenerate -m "..."`
  3. manually review migration for triggers/indexes/dependencies
  4. `python -m alembic upgrade head`
- After importer/schema changes, run import dry-run and idempotency re-run checks.

## Current Status Snapshot
As of this document:
- Baseline coursework API scope is implemented and manually exercised.
- Seed import and endpoint testing are operational.
- pgvector similarity feature is implemented and tested.
- MCP server exposure is implemented.
- Frontend remains deferred.
