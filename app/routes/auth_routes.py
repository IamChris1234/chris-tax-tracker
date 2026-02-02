from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User  # adjust if your User model is elsewhere
from app.auth import hash_password, verify_password  # adjust if names differ

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _is_logged_in(request: Request) -> bool:
    return bool(request.session.get("user_id"))


@router.get("/login")
def login_page(request: Request):
    if _is_logged_in(request):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect email or password"},
            status_code=400,
        )

    request.session["user_id"] = user.id
    request.session["user_email"] = user.email
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/register")
def register_page(request: Request):
    # if you want to ONLY allow first user creation, you can enforce here
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post("/register")
def register(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    email_clean = email.lower().strip()

    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Passwords do not match"},
            status_code=400,
        )

    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "That email is already registered"},
            status_code=400,
        )

    # If your app should only ever have ONE user, uncomment:
    # if db.query(User).count() >= 1:
    #     return templates.TemplateResponse(
    #         "register.html",
    #         {"request": request, "error": "Registration is closed"},
    #         status_code=403,
    #     )

    user_count = db.query(User).count()
    user = User(
        email=email_clean,
        password_hash=hash_password(password),
        # If you have this column; if not, delete next line:
        is_admin=(user_count == 0),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # auto-login after creating account
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email

    return RedirectResponse("/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
