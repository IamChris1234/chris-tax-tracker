from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/receipts")
def receipts(request: Request):
    if not require_login(request):
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("receipts.html", {"request": request})
