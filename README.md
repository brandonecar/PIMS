# PIMS Optimizer

This is a refinery planning project I’ve been building to learn more about how a smaller planning model could work in practice. I’m not trying to recreate Aspen or build some giant enterprise system. The goal is to start with one refinery, one planning period, and a setup that is simple enough to understand and keep improving.

Right now the app is mainly the case setup side:

- creating refinery cases
- storing crude assays and cut data
- storing units, capacities, and yield relationships
- storing products, prices, and simple blend spec rows
- storing streams that tie the planning model together
- loading a demo refinery case for testing
- editing that data through a desktop-style UI

The solve flow and results pages are already there in the app, but the actual LP is the next part I’m working on.

## Stack

- Frontend: Next.js 15, TypeScript, Tailwind CSS v4, AG Grid Community
- Backend: FastAPI, SQLAlchemy 2.0, Alembic
- Database: PostgreSQL 16
- Solver target: PuLP + HiGHS
- Local setup: Docker Compose

## Repo layout

```text
pims-optimizer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── solver/
│   │   └── seed/
│   ├── alembic/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   └── lib/
│   ├── package.json
│   └── Dockerfile
├── data/
├── docker-compose.yml
└── README.md
```

## Running with Docker

Start everything:

```bash
docker-compose up --build
```

Run migrations:

```bash
docker-compose exec backend alembic upgrade head
```

Seed the demo case:

```bash
docker-compose exec backend python -m app.seed.demo_refinery
```

Then open:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Local development without Docker

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

## Main routes

### API

- `GET /api/health`
- `GET/POST /api/cases`
- `GET/PUT/DELETE /api/cases/{id}`
- `POST /api/cases/{id}/clone`
- `GET/POST /api/cases/{id}/crudes`
- `PUT/DELETE /api/crudes/{id}`
- `GET/PUT /api/crudes/{id}/cuts`
- `GET/POST /api/cases/{id}/units`
- `PUT/DELETE /api/units/{id}`
- `GET/PUT /api/units/{id}/yields`
- `GET/POST /api/cases/{id}/products`
- `PUT/DELETE /api/products/{id}`
- `GET/PUT /api/products/{id}/specs`
- `GET/POST /api/cases/{id}/streams`
- `PUT/DELETE /api/streams/{id}`
- `POST /api/cases/{id}/optimize`

### Frontend

- `/cases`
- `/cases/[id]/crudes`
- `/cases/[id]/units`
- `/cases/[id]/products`
- `/cases/[id]/streams`
- `/cases/[id]/economics`
- `/cases/[id]/optimize`
- `/cases/[id]/results`

## Scope for now

I’m keeping this first version pretty narrow on purpose:

- single refinery
- single planning period
- linear model only
- no scheduling
- no tank movements
- no reconciliation/accounting
- no multi-site optimization
- no multi-period inventory logic
- no nonlinear blending
- no auth / permissions

That keeps the first optimization build easier to follow before I add more detail.

## As far as what I’m building next...

The next step is connecting the LP flow:

- pull case data from the database
- build a simplified refinery LP
- solve it with PuLP + HiGHS
- send back crude slate, unit utilization, product volumes, and a margin summary to the UI
