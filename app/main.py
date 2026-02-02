import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.db import engine
from app.models import Base
from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router  # your existing file

def _require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val

# Create tables on startup (simple approach)
Base.metadata.create_all(bind=engine)

app = FastAPI()

SECRET_KEY = _require_env("SECRET_KEY")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,          # Render is HTTPS
    same_site="lax",
)

app.include_router(auth_router)
app.include_router(dashboard_router)

@app.get("/")
def root(request: Request):
    # your dashboard router already handles "/" in your screenshot.
    # This is just a safety fallback if routing changes.
    return RedirectResponse(url="/", status_code=307)
