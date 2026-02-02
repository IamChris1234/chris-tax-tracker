# app/routes/auth_routes.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from ..auth import login as do_login, logout as do_logout, is_logged_in

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if is_logged_in(request):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if do_login(request, username, password):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password."})

@router.get("/logout")
def logout(request: Request):
    do_logout(request)
    return RedirectResponse("/login", status_code=303)

# optional: kill register route so it never breaks anything
@router.get("/register")
def register_disabled():
    return RedirectResponse("/login", status_code=303)

@router.post("/register")
def register_disabled_post():
    return RedirectResponse("/login", status_code=303)
