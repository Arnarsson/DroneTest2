import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .utils.logging import configure_logging
from .db import healthcheck
from .routers import incidents, ingest, embed

load_dotenv()
logger = configure_logging()

app = FastAPI(
    title="DroneWatch API",
    version="0.1.0",
    description="Verified drone incident tracking API with interactive docs and embed support.",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=[
        {"url": "http://localhost:8000", "description": "Development"},
        {"url": "https://api.dronewatch.cc", "description": "Production"}
    ]
)

allowed = [o.strip() for o in os.getenv("ALLOWED_ORIGINS","*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed if allowed != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents.router)
app.include_router(ingest.router)
app.include_router(embed.router)

@app.get("/", tags=["root"])
async def root():
    return {
        "name": "DroneWatch API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/healthz", tags=["health"])
async def health():
    ok = await healthcheck()
    return {"ok": ok, "service": "dronewatch-api"}