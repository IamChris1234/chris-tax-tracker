from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.auth import verify_password, hash_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# --------------------
# LOGIN (GET)
# --------------------
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "register": False,
        },
    )


# --------------------
# LOGIN (POST)
# --------------------
@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password",
                "register": False,
            },
            status_code=401,
        )

    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=303)


# --------------------
# REGISTER (GET)
# --------------------
@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "register": True,
        },
    )


# --------------------
# REGISTER (POST)
# --------------------
@router.post("/register")
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Email already registered",
                "register": True,
            },
            status_code=400,
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
    )

    db.add(user)
    db.commit()

    return RedirectResponse("/login", status_code=303)


# --------------------
# LOGOUT
# --------------------
@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
