# app/auth.py
from fastapi import Request
from sqlalchemy.orm import Session
from .config import APP_USERNAME, APP_PASSWORD

def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("logged_in") is True)

def require_login(request: Request) -> bool:
    return is_logged_in(request)

def login(request: Request, username: str, password: str) -> bool:
    # Password comes from Render env var. Do NOT hardcode in repo.
    if username == APP_USERNAME and password == APP_PASSWORD and APP_PASSWORD:
        request.session["logged_in"] = True
        request.session["username"] = APP_USERNAME
        return True
    return False

def logout(request: Request) -> None:
    request.session.clear()

def get_current_user(request: Request, db: Session):
    # Keep signature compatible with your other routes
    if not is_logged_in(request):
        return None
    return {"username": request.session.get("username", APP_USERNAME)}
