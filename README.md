# Steam-Game-Analytics-API

FastAPI backend for Steam game catalog, search, taxonomy browsing, collections CRUD, and analytics.

## Tech Stack

- FastAPI
- PostgreSQL + SQLAlchemy
- Alembic migrations
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
6. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```

Docs: `http://localhost:8000/docs`  
Health: `http://localhost:8000/api/v1/health`

## Data Workflow

Committed seed dataset:

- `data/seed/steam_games_seed.csv` (350 rows)

Regenerate seed from your full Kaggle CSV:

```bash
python scripts/create_seed_sample.py --input "<path-to-full-kaggle-csv>" --output data/seed/steam_games_seed.csv --size 350 --seed 42
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
- `GET /api/v1/search`
- `GET /api/v1/genres`, `GET /api/v1/genres/{slug}`, `GET /api/v1/genres/{slug}/games`
- `GET /api/v1/tags`, `GET /api/v1/tags/{slug}`, `GET /api/v1/tags/{slug}/games`
- `GET /api/v1/developers`, `GET /api/v1/developers/{slug}`, `GET /api/v1/developers/{slug}/games`
- `GET /api/v1/publishers`, `GET /api/v1/publishers/{slug}`, `GET /api/v1/publishers/{slug}/games`
- `POST/GET/PUT/DELETE /api/v1/collections...` (+ membership endpoints)
- `GET /api/v1/analytics/*`

## Notes

- Docker is required only if you use the compose Postgres path.
- In this local environment, migrations were validated via Alembic offline SQL generation when live Postgres was unavailable.
- Advanced features (pgvector similarity, MCP, frontend) are intentionally deferred.