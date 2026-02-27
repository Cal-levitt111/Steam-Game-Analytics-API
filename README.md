# Steam-Game-Analytics-API

FastAPI backend for Steam game catalog, search, collections, and analytics coursework.

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start PostgreSQL:
   ```bash
   docker compose up -d db
   ```
4. Copy env file:
   ```bash
   copy .env.example .env
   ```
5. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```

API docs: `http://localhost:8000/docs`
Health: `http://localhost:8000/api/v1/health`