import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_models
from app.routers import organizations, scans, findings, risk, reports

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(organizations.router)
app.include_router(scans.router)
app.include_router(findings.router)
app.include_router(risk.router)
app.include_router(reports.router)


@app.on_event("startup")
async def on_startup():
    await init_models()


@app.get("/health")
async def health():
    return {"status": "ok"}
