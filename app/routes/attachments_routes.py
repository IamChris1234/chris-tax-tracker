# app/routes/attachments_routes.py
from datetime import datetime
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user
from ..models import Receipt
from ..storage import save_upload, file_path

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/receipts", response_class=HTMLResponse)
def receipts_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    rows = db.query(Receipt).order_by(Receipt.created_at.desc(), Receipt.id.desc()).all()
    return templates.TemplateResponse("receipts.html", {"request": request, "rows": rows})

@router.post("/receipts/upload")
async def upload_receipt(
    request: Request,
    title: str = Form(...),
    date: str = Form(""),
    note: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    raw = await file.read()
    saved = save_upload(file.filename or "upload", raw)

    d = None
    if date.strip():
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            d = None

    rec = Receipt(
        title=title.strip() or "Receipt",
        date=d,
        note=note.strip() or None,
        filename=saved,
        content_type=file.content_type,
    )
    db.add(rec)
    db.commit()

    return RedirectResponse("/receipts", status_code=303)

@router.get("/receipts/file/{receipt_id}")
def download_receipt(receipt_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    rec = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not rec:
        return RedirectResponse("/receipts", status_code=303)

    path = file_path(rec.filename)
    return FileResponse(path, filename=rec.filename)
