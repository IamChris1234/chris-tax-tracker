from fastapi import Request
from app.config import ADMIN_USERNAME, ADMIN_PASSWORD

def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("logged_in"))

def require_login(request: Request) -> bool:
    return is_logged_in(request)

def check_credentials(username: str, password: str) -> bool:
    # If ADMIN_PASSWORD isn't set, block logins (avoids accidental open deploy)
    if not ADMIN_PASSWORD:
        return False
    return username == (ADMIN_USERNAME or "") and password == ADMIN_PASSWORD
