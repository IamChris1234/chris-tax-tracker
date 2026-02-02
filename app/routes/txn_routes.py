# app/routes/txn_routes.py
from datetime import datetime
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user
from ..models import Transaction

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

CATEGORIES = [
    "Office",
    "Supplies",
    "Meals",
    "Fuel",
    "Repairs & Maintenance",
    "CCA / Capital",
    "Utilities",
    "Insurance",
    "Other",
]

@router.get("/transactions", response_class=HTMLResponse)
def list_transactions(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    rows = db.query(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    return templates.TemplateResponse("transactions.html", {"request": request, "rows": rows})

@router.get("/transactions/new", response_class=HTMLResponse)
def new_transaction(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        "transaction_form.html",
        {"request": request, "categories": CATEGORIES, "error": None, "defaults": {}},
    )

@router.post("/transactions/new")
def create_transaction(
    request: Request,
    date: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse(
            "transaction_form.html",
            {"request": request, "categories": CATEGORIES, "error": "Invalid date.", "defaults": {"description": description, "category": category, "amount": amount}},
        )

    tx = Transaction(date=d, description=description.strip(), category=category, amount=float(amount))
    db.add(tx)
    db.commit()
    return RedirectResponse("/transactions", status_code=303)
