# app/auth.py

from __future__ import annotations

import os
from typing import Optional

from fastapi import Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# If you have a User model in app/models.py, this will work.
# If not, we gracefully return None.
try:
    from .models import User  # type: ignore
except Exception:
    User = None  # type: ignore


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# ---- Single-user login credentials (Render ENV recommended) ----
# DO NOT hardcode your real password in GitHub.
# Put these in Render -> Environment:
#   APP_USERNAME = Chris
#   APP_PASSWORD = (your password)
APP_USERNAME = _env("APP_USERNAME", "Chris")
APP_PASSWORD = _env("APP_PASSWORD", "")


def verify_password(plain_password: str, expected_plain: str) -> bool:
    # For single-user mode we compare plain-to-plain from ENV.
    # (If you later want hashing, we can switch to hashed env var.)
    return plain_password == expected_plain


def get_current_user(request: Request, db: Session) -> Optional[object]:
    """
    Shared helper used by routes.
    Returns a User (DB) if you have one, otherwise returns a small dict.
    Returns None if not logged in.
    """
    user_id = request.session.get("user_id")
    username = request.session.get("username")

    if user_id is None and not username:
        return None

    # If you have a real User table, fetch it
    if User is not None and user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user

    # Otherwise return a simple object-like dict
    return {"id": user_id, "username": username or APP_USERNAME}
