from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.auth import hash_password, verify_password, login_user, logout_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    email_norm = email.strip().lower()
    user = db.query(User).filter(User.email == email_norm).first()

    # IMPORTANT: avoid leaking which part is wrong in production; but ok for now.
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect email or password."},
            status_code=401,
        )

    login_user(request, user)
    return RedirectResponse(url="/", status_code=303)

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
def register_submit(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    email_norm = email.strip().lower()

    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match."},
            status_code=400,
        )

    existing = db.query(User).filter(User.email == email_norm).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "That email is already registered."},
            status_code=400,
        )

    # First user becomes admin (optional but handy)
    is_first_user = db.query(User).count() == 0

    user = User(
        email=email_norm,
        password_hash=hash_password(password),
        is_admin=is_first_user,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-login after register
    login_user(request, user)
    return RedirectResponse(url="/", status_code=303)

@router.get("/logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse(url="/login", status_code=303)
