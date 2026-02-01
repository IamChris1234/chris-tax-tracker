from datetime import date
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user
from ..models import Transaction

router = APIRouter(prefix="/transactions")
templates = Jinja2Templates(directory="app/templates")

@router.get("")
def list_tx(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    items = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.date.desc()).limit(200).all()
    return templates.TemplateResponse("transactions.html", {"request": request, "items": items})

@router.get("/new")
def new_tx_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("transaction_form.html", {"request": request})

@router.post("/new")
def create_tx(
    request: Request,
    date_str: str = Form(...),
    vendor: str = Form(""),
    description: str = Form(""),
    amount: float = Form(...),
    type: str = Form("General"),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    d = date.fromisoformat(date_str)
    tx = Transaction(
        user_id=user.id,
        date=d,
        vendor=vendor,
        description=description,
        amount=amount,
        type=type,
        notes=notes,
    )
    db.add(tx)
    db.commit()
    return RedirectResponse("/transactions", status_code=303)
