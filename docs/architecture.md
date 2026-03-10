# Architecture Rationale

## System Shape

The project is split into a backend API and a frontend application:

- FastAPI backend in `app/`
- Next.js frontend in `frontend/`
- PostgreSQL + pgvector for persistent storage
- Alembic for schema evolution

The backend follows a layered design:

- Routers: HTTP parsing, dependency wiring, and response shaping
- Services: domain rules such as ownership checks and conflict handling
- Repositories: SQLAlchemy query construction and aggregate query logic
- Models: SQLAlchemy tables/entities
- Schemas: Pydantic request and response models

This keeps business rules out of route handlers and keeps query logic isolated enough to test with targeted fixtures.

## Data Model

The database is normalised around a central `games` table plus independent dimensions and junction tables:

- Core tables: `games`, `users`, `collections`
- Taxonomy dimensions: `genres`, `tags`, `developers`, `publishers`, `categories`
- Junction tables: `game_genres`, `game_tags`, `game_developers`, `game_publishers`, `game_categories`, `collection_games`
- Auth/rate-limit support: `auth_rate_limit_counters`

Current game records store the canonical long-form description in `about_the_game`. The schema also includes extended metadata such as price, platform support, review counts, support details, media links, and a `VECTOR(384)` embedding for similarity search.

## Query And Indexing Strategy

Key performance-oriented design decisions:

- PostgreSQL full-text search uses `games.search_vector` maintained by a trigger over weighted game fields and related tag text.
- Search/filter indexes are present on `search_vector`, `metacritic_score`, `release_date`, and `price_usd`.
- Junction-table foreign keys are indexed to support taxonomy lookups and joins.
- pgvector uses an IVFFlat cosine index on `games.embedding` for similar-game queries.

These choices support the coursework’s read-heavy catalogue/search/analytics use cases without denormalising the source data.

## Request Flow

Typical backend request flow:

1. A router validates path/query/body data and applies auth dependencies.
2. A database session is injected with `get_db`.
3. Service code enforces domain rules and raises `AppException` for expected failures.
4. Repository code performs ORM or SQL queries.
5. Routers serialise models into the expected response envelope or typed response model.

Errors are normalised in `app/core/error_handlers.py` to:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "...",
    "detail": null
  }
}
```

## Authentication Model

The runtime now uses an environment-aware access model:

- In development, interactive docs are enabled and read-only backend routes stay public for local testing.
- In production, `POST /api/v1/auth/register` and `POST /api/v1/auth/login` are the only public bootstrap routes.
- In production, all remaining backend routes require JWT bearer authentication.
- JWT access tokens are signed with RS256 and include a `kid` header.
- JWKS publication remains available at `/.well-known/jwks.json`; it is protected in production.
- Login and register requests are rate-limited with database-backed counters.

The frontend mirrors this with a BFF pattern:

- Next.js route handlers call the FastAPI auth endpoints.
- The resulting bearer token is stored in an HTTP-only cookie (`sga_session`).
- Server components and server actions read that cookie and forward the token to the backend.
- Every frontend page except `/auth` requires a valid session.

## MCP Design

When `ENABLE_MCP_SERVER=true`, the app mounts an MCP transport at `/mcp` and `/mcp/messages/`:

- Only read-only tags are exposed as tools: `health`, `games`, `search`, `genres`, `tags`, `developers`, `publishers`, `analytics`
- `auth` and `collections` are intentionally excluded
- The MCP transport is auth-gated using the same FastAPI auth dependency

## Deliberate Runtime Choices

- Interactive runtime docs are enabled only in development.
- The API remains versioned under `/api/v1`.
- Import scripts are idempotent and support both seed and full-dataset workflows.
- Embeddings are generated offline instead of during request handling.

## Current Limitations

- Many tests use SQLite fixtures for fast feedback, so full fidelity remains PostgreSQL-first.
- Similarity quality depends on embedding coverage and model choice.
- Search quality depends on the completeness of imported text and taxonomy data.
- The frontend currently uses single access-token sessions rather than refresh-token rotation.

## Suggested Next Additions

1. Add a Postgres-backed CI job that runs the full integration suite against the real schema.
2. Add deployment-specific runbooks for the final hosting target.
3. Add observability around expensive analytics and similarity queries before public launch.
