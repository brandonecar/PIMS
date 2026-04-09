# PIMS Optimizer

A simplified PIMS-style refinery planning application. Built as a learning project
to explore refinery economics, LP optimization, and practical software structure.

Single refinery, single planning period, linear model. Not a clone of Aspen PIMS —
a focused, approachable planning tool that demonstrates the core concepts.

## What it does

- Define crude assays with distillation cuts and sulfur properties
- Configure process units (CDU, VDU, FCC, Reformer, Hydrotreater) with yield structures
- Set product specifications, prices, and demand bounds
- Run an LP optimizer that maximizes gross margin subject to:
  - Material balance on all streams
  - Unit capacity constraints
  - Product demand bounds
  - Sulfur blend quality constraints
- View results: crude slate, unit utilization, product outputs, margin breakdown

## Stack

- **Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS 4, AG Grid
- **Backend:** FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- **Database:** PostgreSQL 16
- **Solver:** PuLP + HiGHS (falls back to CBC if highspy unavailable)

## Running locally with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

The backend automatically runs migrations and seeds a demo refinery case on first start.
Docker Compose sets `ENVIRONMENT=development` for hot reload.

## Running without Docker

### Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python -m app.seed.demo_refinery
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## Running tests

```bash
cd backend
python -m pytest tests/ -v
```

Tests use SQLite in-memory (no Postgres required). Currently 20 passing tests
covering solver logic, sulfur constraints, and API integration.

## Deploying to production

Recommended architecture: **Vercel** (frontend) + **Render** (backend + Postgres).

### Render (backend + database)

1. Create a new **Blueprint** on Render and point it at this repo.
   The `render.yaml` in the repo root defines a web service (`pims-api`) and
   a free Postgres database (`pims-db`).

2. After creation, update the `CORS_ORIGINS` env var on the `pims-api` service
   to your actual Vercel frontend URL:
   ```
   CORS_ORIGINS=["https://your-app.vercel.app"]
   ```

3. The backend will automatically run migrations and seed the demo case on first
   deploy (controlled by `SEED_DEMO_DATA=true`). Set it to `false` after first
   deploy if you don't want re-seeding on empty databases.

The `render.yaml` wires `DATABASE_URL` from the managed Postgres instance
automatically. The backend normalizes `postgres://` URLs to
`postgresql+psycopg2://` so no manual URL editing is needed.

### Vercel (frontend)

1. Import the repo on Vercel. Set the **Root Directory** to `frontend`.

2. Add one environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://pims-api.onrender.com
   ```
   (Use your actual Render service URL.)

3. Vercel auto-detects Next.js and runs `npm run build`. No other config needed.

`NEXT_PUBLIC_API_URL` is baked into the frontend at build time. If you change
the backend URL, you need to redeploy the frontend.

### Environment variables reference

**Backend (`pims-api`):**

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Postgres connection string | localhost dev DB |
| `CORS_ORIGINS` | Yes | JSON list of allowed origins | `["http://localhost:3000"]` |
| `SEED_DEMO_DATA` | No | Seed demo case on empty DB | `true` |
| `ENVIRONMENT` | No | `development` enables --reload | `production` |

**Frontend:**

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes (prod) | Backend API base URL | `http://localhost:8000` |

## Scope

Intentionally narrow for v1:
- Single refinery, single planning period
- Linear model only (no MILP, no nonlinear blending)
- Sulfur is the only quality property enforced
- No auth, no multi-user, no scheduling
- No tank movements, reconciliation, or multi-site optimization
