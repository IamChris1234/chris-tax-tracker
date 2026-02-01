from datetime import date
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user
from ..models import FuelEntry

router = APIRouter(prefix="/fuel")
templates = Jinja2Templates(directory="app/templates")

@router.get("")
def fuel_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    items = db.query(FuelEntry).filter(FuelEntry.user_id == user.id).order_by(FuelEntry.date.desc()).limit(200).all()
    return templates.TemplateResponse("fuel.html", {"request": request, "items": items})

@router.get("/new")
def fuel_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("fuel_form.html", {"request": request})

@router.post("/new")
def fuel_create(
    request: Request,
    date_str: str = Form(...),
    amount: float = Form(...),
    odo: int = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    d = date.fromisoformat(date_str)
    f = FuelEntry(user_id=user.id, date=d, amount=amount, odo=odo, notes=notes)
    db.add(f)
    db.commit()
    return RedirectResponse("/fuel", status_code=303)
