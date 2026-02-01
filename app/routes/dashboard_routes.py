from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import get_current_user
from ..models import Transaction, FuelEntry, Receipt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    tx_count = db.query(Transaction).filter(Transaction.user_id == user.id).count()
    fuel_count = db.query(FuelEntry).filter(FuelEntry.user_id == user.id).count()
    receipt_count = db.query(Receipt).filter(Receipt.user_id == user.id).count()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "tx_count": tx_count,
        "fuel_count": fuel_count,
        "receipt_count": receipt_count,
    })
