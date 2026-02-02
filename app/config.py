# app/config.py
import os

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)

APP_USERNAME = env("APP_USERNAME", "Chris")
APP_PASSWORD = env("APP_PASSWORD", "")  # must be set on Render (do NOT commit)
SESSION_SECRET = env("SESSION_SECRET", "change-me-in-render")  # set on Render

DATABASE_URL = env("DATABASE_URL", "")  # set on Render for Postgres
