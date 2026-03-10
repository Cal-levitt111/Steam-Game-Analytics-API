# Steam-Game-Analytics-API

Steam Game Analytics is a coursework project built around a FastAPI backend and a Next.js frontend for exploring Steam catalogue data, full-text search, similarity recommendations, user collections, and analytics.

## Delivered Scope

- Normalised PostgreSQL schema with games, taxonomy dimensions, junction tables, users, collections, and collection membership.
- JWT bearer authentication with RS256 signing, JWKS publication, profile lookup/update, and database-backed auth rate limiting.
- Read-only catalogue, search, taxonomy, and analytics endpoints.
- Full CRUD for authenticated user collections plus collection membership add/remove.
- pgvector-powered similar-game recommendations with offline embedding generation.
- Next.js frontend with a BFF-style auth layer that stores the API token in an HTTP-only cookie.
- Optional MCP server mount with read-only tool exposure.

API base path: `/api/v1`

## Access Model

- In `ENVIRONMENT=development`, Swagger/OpenAPI is available at `/docs`, `/redoc`, and `/openapi.json`.
- In `ENVIRONMENT=development`, read-only backend routes are public for easier local testing.
- In `ENVIRONMENT=development`, routes that explicitly declare bearer auth still appear as protected in Swagger UI and can be exercised with the `Authorize` button.
- In `ENVIRONMENT=production`, `POST /api/v1/auth/register` and `POST /api/v1/auth/login` are the only public backend endpoints.
- In `ENVIRONMENT=production`, all other backend routes require a valid bearer token, including health, JWKS, collections/public, analytics, taxonomy, and MCP when enabled.
- The frontend only leaves `/auth` publicly accessible. All other application pages redirect to `/auth` when there is no valid session.
- Interactive runtime docs are intentionally disabled outside development so the hosted app does not expose an unauthenticated API surface.

## Stack

- Python 3.12
- FastAPI + Starlette
- SQLAlchemy 2.x + Alembic
- PostgreSQL 16 + pgvector
- `python-jose` + `cryptography`
- Pandas + sentence-transformers
- Next.js 16 + React 19 + TypeScript
- Pytest, Vitest, Playwright

## Repository Layout

- `app/`: backend application code
- `app/core/`: config, auth, DB session, security middleware, error handling
- `app/routers/`: HTTP endpoints
- `app/services/`: business rules
- `app/repositories/`: query/data-access layer
- `app/models/`: SQLAlchemy models and association tables
- `app/schemas/`: Pydantic request/response contracts
- `alembic/`: migration history
- `scripts/`: import, seed, and embedding generation utilities
- `frontend/`: Next.js frontend
- `tests/`: backend tests
- `docs/`: architecture, endpoint matrix, and deployment runbooks

## Prerequisites

- Python 3.12
- Node.js 20+
- Docker Desktop or another Docker runtime for the local Postgres container

## Backend Setup

1. Create and activate a virtual environment.
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install Python dependencies.
   ```powershell
   pip install -r requirements.txt
   ```
3. Create the backend environment file.
   ```powershell
   Copy-Item .env.example .env
   ```
4. Start PostgreSQL.
   ```powershell
   docker compose up -d db
   ```
5. Apply migrations.
   ```powershell
   python -m alembic upgrade head
   ```
6. Import the seed dataset.
   ```powershell
   python scripts/import_games.py --mode seed
   ```
7. Generate embeddings for the similarity endpoint.
   ```powershell
   python scripts/generate_embeddings.py --mode seed --only-missing
   ```
8. Start the API.
   ```powershell
   uvicorn app.main:app --reload
   ```

If Postgres reports a collation mismatch after switching images, recreate the volume:

```powershell
docker compose down -v
docker compose up -d db
```

## Frontend Setup

1. Create the frontend environment file.
   ```powershell
   Copy-Item frontend\.env.example frontend\.env.local
   ```
2. Install frontend dependencies.
   ```powershell
   Set-Location frontend
   npm install
   ```
3. Start the frontend.
   ```powershell
   npm run dev
   ```

Default local URLs:

- Frontend: `http://localhost:3000`
- Backend: `http://127.0.0.1:8000`
- Local API docs: `http://127.0.0.1:8000/docs`
- Local ReDoc: `http://127.0.0.1:8000/redoc`
- Local OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Local Run Flow

1. Start the backend and frontend using the setup steps above.
2. Open `http://localhost:3000/auth`.
3. Register a user or sign in with an existing account.
4. Browse the authenticated frontend routes:
   - `/`
   - `/games`
   - `/games/[id]`
   - `/search`
   - `/analytics`
   - `/mcp`
   - `/collections`
   - `/collections/public`
   - `/collections/[id]`

## API Docs

Hosted/generated API docs: `<add generated API docs link here>`

In local development, FastAPI serves Swagger at `/docs`, ReDoc at `/redoc`, and the raw OpenAPI schema at `/openapi.json`.

Swagger UI shows the protected routes and lets testers paste a bearer token into the `Authorize` dialog instead of calling protected endpoints manually with `curl`.

If you need to generate the schema file manually for external documentation generation:

```powershell
python -c "import json; from app.main import app; print(json.dumps(app.openapi(), indent=2))" > openapi.json
```

## Local MCP Testing In VS Code

To test the MCP server locally in VS Code:

1. Start the backend locally with:
   ```powershell
   uvicorn app.main:app --reload
   ```
2. Confirm the MCP mount is reachable at `http://127.0.0.1:8000/mcp`.
3. Create or update `.vscode/mcp.json` in the repository root:
   ```json
   {
     "servers": {
       "steam-api": {
         "type": "http",
         "url": "http://127.0.0.1:8000/mcp"
       }
     }
   }
   ```
4. Reload VS Code if the MCP server is not detected immediately.
5. Use the MCP server from your VS Code MCP workflow.

Local development leaves the MCP mount open for testing. In production, when MCP is enabled, the mount is protected by bearer authentication.

## Coursework Alignment

- CRUD requirement: implemented through collections create/read/update/delete plus membership add/remove.
- Authentication requirement: JWT bearer auth is enforced across the application surface outside the login/register bootstrap routes.
- SQL database requirement: PostgreSQL schema is normalised with junction tables and migration history in Alembic.
- Advanced querying requirement: full-text search, pgvector similarity, and aggregation-heavy analytics endpoints are implemented.
- Testing requirement: backend pytest suite plus frontend unit and end-to-end tests are included.
- Documentation requirement: README, architecture notes, deployment checklist, and endpoint/coursework mapping are maintained in `docs/`.

## Testing

Backend:

```powershell
python -m pytest -q
```

Frontend:

```powershell
Set-Location frontend
npm run lint
npm run typecheck
npm run test:unit
```

Optional frontend E2E verification:

```powershell
Set-Location frontend
npx playwright install chromium
npm run test:e2e
```

## Security And Deployment Notes

- The app refuses to start in production without `FORCE_HTTPS`, `ALLOWED_HOSTS`, a non-placeholder `SECRET_KEY`, and active JWT key material.
- Auth endpoints are rate-limited by database-backed counters.
- JWKS remains available for key verification. It is public in development and protected in production.
- `ENABLE_MCP_SERVER=false` is the safest default for deployment. If enabled, the MCP transport is still auth-gated.
- See [docs/production-security-checklist.md](docs/production-security-checklist.md) before deployment.

## Supporting Docs

- [docs/architecture.md](docs/architecture.md)
- [docs/endpoint-matrix.md](docs/endpoint-matrix.md)
- [docs/production-security-checklist.md](docs/production-security-checklist.md)
- [docs/jwt-key-rotation-runbook.md](docs/jwt-key-rotation-runbook.md)
- [frontend/README.md](frontend/README.md)
