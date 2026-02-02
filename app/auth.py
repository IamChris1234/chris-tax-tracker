from passlib.context import CryptContext
from fastapi import Request
from sqlalchemy.orm import Session
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SESSION_USER_KEY = "user_id"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def login_user(request: Request, user: User) -> None:
    request.session[SESSION_USER_KEY] = user.id

def logout_user(request: Request) -> None:
    request.session.pop(SESSION_USER_KEY, None)

def get_current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get(SESSION_USER_KEY)
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()
