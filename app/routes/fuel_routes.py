from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/fuel")
def fuel(request: Request):
    if not require_login(request):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("fuel.html", {"request": request})
