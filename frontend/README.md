# Steam Game Analytics Demo Frontend

Minimal Next.js frontend for demonstrating and testing the FastAPI backend in this repository.

## What it covers

- Public demo pages for catalog browsing, search, game detail, similarity, public collections, and analytics
- Authenticated flows for login, registration, personal collections, and collection membership changes
- A BFF auth layer that stores the FastAPI bearer token in an HTTP-only cookie instead of exposing it to browser code

## Backend prerequisites

Run these commands from the repository root before starting the frontend:

1. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create the backend environment file:
   ```bash
   copy .env.example .env
   ```
3. Start PostgreSQL:
   ```bash
   docker compose up -d db
   ```
4. Apply migrations:
   ```bash
   python -m alembic upgrade head
   ```
5. Import the seed dataset:
   ```bash
   python scripts/import_games.py --mode seed
   ```
6. Generate embeddings for the similarity endpoint:
   ```bash
   python scripts/generate_embeddings.py --mode seed --only-missing
   ```
7. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

Useful backend URLs:

- Swagger docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/v1/health`

## Frontend setup

1. Create the frontend environment file:
   ```bash
   copy .env.example .env.local
   ```
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Start the demo app:
   ```bash
   npm run dev
   ```

Default frontend URL: `http://localhost:3000`  
Default backend URL: `http://127.0.0.1:8000`

## Demo routes

- `/`
- `/auth`
- `/games`
- `/search`
- `/games/[id]`
- `/collections`
- `/collections/public`
- `/collections/[id]`
- `/analytics`

## Scripts

- `npm run dev`
- `npm run build`
- `npm run start`
- `npm run lint`
- `npm run typecheck`
- `npm run test`
- `npm run test:unit`
- `npm run test:e2e`

## Verification workflow

Use this sequence after backend startup:

1. Confirm the API health endpoint returns `ok`.
2. Open `http://localhost:3000/` and verify featured games and analytics preview cards are populated.
3. Register a demo account on `/auth`.
4. Create a collection on `/collections`.
5. Open a game detail page and add the game to the collection.
6. Visit `/analytics` and confirm the dashboard renders charts and summary cards.

For automated checks:

```bash
npm run lint
npm run typecheck
npm run build
npm run test:unit
npx playwright install chromium
npm run test:e2e
```

`npm run test:e2e` starts its own Next dev server on `http://127.0.0.1:3100` so it does not collide with anything already listening on port `3000`.

## Known limitations

- The frontend assumes the backend is already migrated and seeded.
- Similarity gracefully degrades when embeddings are missing, but the full demo is better when `scripts/generate_embeddings.py --mode seed --only-missing` has been run.
- Auth uses a single access-token cookie. Refresh tokens and deployment-specific auth hardening are intentionally out of scope for this demo app.
