# Architecture Rationale, Limitations, and Deferred Features

## Architecture Rationale

The backend uses a layered structure:

- Routers: HTTP concerns only (query/path parsing, auth dependencies, response wrapping)
- Services: business rules (ownership checks, visibility checks, conflict handling)
- Repositories: SQLAlchemy query logic and aggregation queries
- Models: SQLAlchemy ORM entities + association tables
- Schemas: Pydantic request/response contracts

This separation keeps endpoint handlers thin and makes query logic testable in isolation.

## Key Design Decisions

- API base path is versioned: `/api/v1`
- Developer/publisher relationship is many-to-many only (junction-table model)
- Search uses PostgreSQL FTS (`search_vector` + rank query) with SQLite fallback for tests
- A follow-up hardening migration restores search/filter indexes at head (`ix_games_search_vector`, `ix_games_metacritic_score`, `ix_games_release_date`, `ix_games_price_usd`)
- Similar-game recommendations use pgvector cosine distance (`/games/{id}/similar`)
- Data import is idempotent (`ON CONFLICT` strategy) and supports `seed` and `full` modes
- Error responses use a consistent envelope for machine-friendly client handling

## Current Limitations

- Runtime validation against a live Postgres instance was not always available in this environment, so migrations were also validated with Alembic offline SQL generation.
- Several tests use SQLite compatibility fixtures; production behavior is still PostgreSQL-first.
- Search ranking quality depends on imported text completeness and search-vector refresh quality.
- Pagination links are generated as relative API paths and assume `api/v1` routing.

## Deferred Features (Intentional)

- MCP server exposure (`/mcp`)
- Next.js frontend
- Rate limiting / Redis caching
- Cloud deployment playbooks (Render/Railway) as production runbook docs

## Suggested Next Additions

1. Add a Postgres-backed CI job using a service container and execute full migration + integration tests there.
2. Add benchmark scripts for import runtime and heavy analytics endpoint timings.
3. Add role-based authorization hooks if coursework scope expands.
