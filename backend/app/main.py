"""Blood Donation Manager — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth

app = FastAPI(
    title="Blood Donation Manager",
    description="API for coordinating blood donation requests and donor profiles.",
    version="0.1.0",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allows the React dev server (port 5173) to call the API.
# Restrict origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api")


@app.get("/", tags=["health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "service": "Blood Donation Manager API"}
