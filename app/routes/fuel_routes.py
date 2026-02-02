# app/routes/fuel_routes.py
from datetime import datetime
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user
from ..models import FuelEntry

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/fuel", response_class=HTMLResponse)
def fuel_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    rows = db.query(FuelEntry).order_by(FuelEntry.date.desc(), FuelEntry.id.desc()).all()
    return templates.TemplateResponse("fuel.html", {"request": request, "rows": rows})

@router.get("/fuel/new", response_class=HTMLResponse)
def fuel_new(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("fuel_form.html", {"request": request, "error": None, "defaults": {}})

@router.post("/fuel/new")
def fuel_create(
    request: Request,
    date: str = Form(...),
    liters: float = Form(...),
    cost: float = Form(...),
    odometer: int = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse(
            "fuel_form.html",
            {"request": request, "error": "Invalid date.", "defaults": {"liters": liters, "cost": cost, "odometer": odometer, "note": note}},
        )

    row = FuelEntry(date=d, liters=float(liters), cost=float(cost), odometer=int(odometer), note=note.strip() or None)
    db.add(row)
    db.commit()
    return RedirectResponse("/fuel", status_code=303)
