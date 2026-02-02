from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# HARD-CODED CREDENTIALS
USERNAME = "Chris"
PASSWORD = "canGG6825"


def is_logged_in(request: Request) -> bool:
    return request.session.get("logged_in") is True


@router.get("/login")
def login_page(request: Request):
    if is_logged_in(request):
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None},
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == USERNAME and password == PASSWORD:
        request.session["logged_in"] = True
        return RedirectResponse("/dashboard", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Incorrect username or password"},
        status_code=401,
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
