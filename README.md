# Steam-Game-Analytics-API

FastAPI backend for Steam game catalog, search, taxonomy browsing, collections CRUD, and analytics.

## Tech Stack

- FastAPI
- PostgreSQL + SQLAlchemy
- pgvector (Postgres extension)
- fastapi-mcp (MCP server mount)
- Alembic migrations
- sentence-transformers (local embedding generation)
- Pytest + TestClient

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy environment file:
   ```bash
   copy .env.example .env
   ```
3. Start PostgreSQL (Docker path):
   ```bash
   docker compose up -d db
   ```
4. Run migrations:
   ```bash
   python -m alembic upgrade head
   ```
5. Import seed dataset:
   ```bash
   python scripts/import_games.py --mode seed
   ```
6. Generate seed embeddings (for similar-games endpoint):
   ```bash
   python scripts/generate_embeddings.py --mode seed --only-missing
   ```
7. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```

If you see a Postgres collation mismatch warning after switching images, recreate volumes:

```bash
docker compose down -v
docker compose up -d db
```

Docs: `http://localhost:8000/docs`  
Health: `http://localhost:8000/api/v1/health`

## Data Workflow

Committed seed dataset:

- `data/seed/steam_game_seed_1000_2.csv` (1000 rows)

Regenerate seed from your full Kaggle CSV:

```bash
python scripts/generate_seed_from_dataset.py --n 1000 --seed 42 --out data/seed/steam_game_seed_1000_2.csv
```

Import modes:

- Seed import:
  ```bash
  python scripts/import_games.py --mode seed
  ```
- Full import:
  ```bash
  python scripts/import_games.py --mode full --input "<path-to-full-kaggle-csv>"
  ```
- Dry run (no writes):
  ```bash
  python scripts/import_games.py --mode seed --dry-run
  ```

## Running Tests

Run full suite:

```bash
python -m pytest -q
```

Run targeted suites:

```bash
python -m pytest tests/test_auth.py -q
python -m pytest tests/test_collections.py -q
python -m pytest tests/test_analytics.py -q
```

## Current API Coverage

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `PUT /api/v1/auth/me`
- `GET /api/v1/games`
- `GET /api/v1/games/{id}`
- `GET /api/v1/games/{id}/similar`
- `GET /api/v1/search`
- `MCP server mount at /mcp` (read-only tool exposure)
- `GET /api/v1/genres`, `GET /api/v1/genres/{slug}`, `GET /api/v1/genres/{slug}/games`
- `GET /api/v1/tags`, `GET /api/v1/tags/{slug}`, `GET /api/v1/tags/{slug}/games`
- `GET /api/v1/developers`, `GET /api/v1/developers/{slug}`, `GET /api/v1/developers/{slug}/games`
- `GET /api/v1/publishers`, `GET /api/v1/publishers/{slug}`, `GET /api/v1/publishers/{slug}/games`
- `POST/GET/PUT/DELETE /api/v1/collections...` (+ membership endpoints)
- `GET /api/v1/analytics/*`

## Similar Endpoint Notes

- Endpoint: `GET /api/v1/games/{id}/similar?limit=10`
- Query params: `limit` (default `10`, min `1`, max `50`)
- Expected errors:
  - `404 RESOURCE_NOT_FOUND` for missing `id`
  - `409 EMBEDDING_NOT_AVAILABLE` when target game has no embedding
  - `501 FEATURE_UNAVAILABLE` when vector support/config is unavailable

## MCP Notes

- MCP server is mounted at `/mcp`.
- Exposure is intentionally read-only by tag allowlist:
  - `health`, `games`, `search`, `genres`, `tags`, `developers`, `publishers`, `analytics`
- Auth and collections write flows are excluded from MCP tool exposure.
- VS Code Copilot MCP config is provided in `.vscode/mcp.json` (URL: `http://127.0.0.1:8000/mcp`).

## Notes

- Docker is required only if you use the compose Postgres path.
- In this local environment, migrations were validated via Alembic offline SQL generation when live Postgres was unavailable.
- Head migrations include index hardening for search/filter workloads (`ix_games_search_vector`, `ix_games_metacritic_score`, `ix_games_release_date`, `ix_games_price_usd`).
- Head migrations also include pgvector enablement and game embedding index (`ix_games_embedding_ivfflat_cosine`).
- Frontend work is intentionally deferred.
