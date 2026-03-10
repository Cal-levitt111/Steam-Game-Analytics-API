# Steam Game Analytics Frontend

This is the Next.js frontend for the Steam Game Analytics project. It sits in front of the FastAPI backend and uses a BFF-style auth layer so the browser never stores the API bearer token directly.

## Frontend Scope

- Login and registration flows through `app/api/auth/*`
- Session handling with an HTTP-only `sga_session` cookie
- Auth-gated catalogue, search, analytics, and collection pages
- Collection create/update/membership actions through Next.js server actions
- Server-side data fetching against the protected FastAPI API

## Access Model

- `/auth` is the only public application page.
- Every other page redirects to `/auth` when there is no valid session.
- The frontend forwards the stored bearer token to every backend request, including read-only pages such as games, analytics, search, and public collections.

## Backend Prerequisites

Run these commands from the repository root before starting the frontend:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d db
python -m alembic upgrade head
python scripts/import_games.py --mode seed
python scripts/generate_embeddings.py --mode seed --only-missing
uvicorn app.main:app --reload
```

## Frontend Setup

Run these commands from `frontend/`:

```powershell
Copy-Item .env.example .env.local
npm install
npm run dev
```

Local URLs:

- Frontend: `http://localhost:3000`
- Backend: `http://127.0.0.1:8000`

## Available Routes

- `/auth`
- `/`
- `/games`
- `/games/[id]`
- `/search`
- `/analytics`
- `/collections`
- `/collections/public`
- `/collections/[id]`

## Verification Flow

1. Start the backend and frontend.
2. Open `http://localhost:3000/` and confirm it redirects to `/auth`.
3. Register an account on `/auth`.
4. Create a collection on `/collections`.
5. Open a game detail page and add the game to the collection.
6. Open `/analytics` and `/search` to verify authenticated read-only pages load successfully.

## Scripts

- `npm run dev`
- `npm run build`
- `npm run start`
- `npm run lint`
- `npm run typecheck`
- `npm run test`
- `npm run test:unit`
- `npm run test:e2e`

## Automated Checks

```powershell
npm run lint
npm run typecheck
npm run build
npm run test:unit
npx playwright install chromium
npm run test:e2e
```

`npm run test:e2e` starts its own Next dev server on `http://127.0.0.1:3100`.

## Notes

- The frontend assumes the backend database is already migrated and seeded.
- Similarity works best after embedding generation has been run.
- Auth currently uses a single access-token cookie rather than refresh tokens.
