import os
from pathlib import Path

def env(key: str, default: str | None = None) -> str:
    v = os.getenv(key, default)
    if v is None:
        raise RuntimeError(f"Missing required env var: {key}")
    return v

APP_NAME = os.getenv("APP_NAME", "Chris Tax Tracker")
SECRET_KEY = env("SECRET_KEY", "dev-secret-change-me")  # set real one on Render

# Render/Neon will provide DATABASE_URL like:
# postgres://user:pass@host/db?sslmode=require
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# Upload storage:
# On Render, set STORAGE_PATH to your mounted disk path (e.g. /data)
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "./storage")).resolve()
UPLOADS_DIR = STORAGE_PATH / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
