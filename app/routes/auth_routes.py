from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..auth import verify_password, hash_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid login"})
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# optional: quick bootstrap endpoint (delete later)
@router.get("/init-admin")
def init_admin(db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == "admin@local").first()
    if existing:
        return {"ok": True, "msg": "already exists"}
    u = User(email="admin@local", password_hash=hash_password("admin123"))
    db.add(u)
    db.commit()
    return {"ok": True, "email": "admin@local", "password": "admin123"}
