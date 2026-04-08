# PIMS Optimizer

This is a refinery planning project I’ve been building to learn how a smaller planning model could work in practice. It started from an Excel model I built in my Petrochemical & Refining Economics class, and I wanted to take it further beyond the limits of the Solver Add-In. The goal is to start with one refinery, one planning period, and a setup that’s simple enough to understand while still leaving room to improve and expand.

Right now the app handles mainly the case setup side:
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

## Running with Docker

```bash
docker-compose up --build
```

```bash
docker-compose exec backend alembic upgrade head
```

```bash
docker-compose exec backend python -m app.seed.demo_refinery
```

Then open:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

## Scope for now

I’m keeping this first version pretty narrow on purpose:

- single refinery
- single planning period
- linear model only
- no scheduling or tank logic
- no multi-site or multi-period setup
- no auth

That keeps the first optimization build easier to follow before I add more detail.

## As far as what I’m building next...

The next step is connecting the LP flow:

- pull case data from the database
- build a simplified refinery LP
- solve it with PuLP + HiGHS
- send back crude slate, unit utilization, product volumes, and a margin summary to the UI
