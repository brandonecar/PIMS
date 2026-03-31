from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import cases, crudes, units, products, streams, solver

app = FastAPI(title="PIMS Optimizer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(crudes.router)
app.include_router(units.router)
app.include_router(products.router)
app.include_router(streams.router)
app.include_router(solver.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
