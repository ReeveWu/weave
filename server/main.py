"""Weave FastAPI server.

Start with:
    uvicorn server.main:app --reload --port 8000
(run from the project root, i.e. the Weave/ directory)
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.pipeline import router as pipeline_router

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def _get_cors_origins() -> list[str]:
    """Return comma-separated CORS origins from env, with local dev defaults."""
    origins = os.getenv("CORS_ORIGINS")
    if not origins:
        return DEFAULT_CORS_ORIGINS

    parsed_origins = []
    for origin in origins.split(","):
        origin = origin.strip().rstrip("/")
        if origin:
            parsed_origins.append(origin)

    return parsed_origins or DEFAULT_CORS_ORIGINS


app = FastAPI(
    title="Weave API",
    description="Backend API for the Weave PDF-to-Handout web interface.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the Next.js dev server and production build
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(pipeline_router)


@app.get("/health")
async def health() -> dict:
    """Simple liveness probe."""
    return {"status": "ok"}
