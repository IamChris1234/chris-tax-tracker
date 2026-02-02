from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(request: Request):
    if not request.session.get("logged_in"):
        return RedirectResponse("/login", status_code=303)

    # use your existing dashboard.html (the nicer one you already have)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request},
    )
