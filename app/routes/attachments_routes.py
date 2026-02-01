import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user
from ..models import Receipt
from ..config import UPLOADS_DIR

router = APIRouter(prefix="/receipts")
templates = Jinja2Templates(directory="app/templates")

@router.get("")
def receipts_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    items = db.query(Receipt).filter(Receipt.user_id == user.id).order_by(Receipt.uploaded_at.desc()).limit(200).all()
    return templates.TemplateResponse("import_rr60.html", {"request": request, "items": items})  # re-use if you want

@router.post("/upload")
def upload_receipt(
    request: Request,
    file: UploadFile = File(...),
    transaction_id: int | None = Form(None),
    fuel_entry_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    ext = Path(file.filename).suffix.lower()
    stored = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOADS_DIR / stored

    contents = file.file.read()
    dest.write_bytes(contents)

    r = Receipt(
        user_id=user.id,
        original_name=file.filename,
        stored_name=stored,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(contents),
        transaction_id=transaction_id,
        fuel_entry_id=fuel_entry_id,
        uploaded_at=datetime.utcnow(),
    )
    db.add(r)
    db.commit()
    return RedirectResponse("/receipts", status_code=303)

@router.get("/download/{receipt_id}")
def download_receipt(receipt_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    r = db.get(Receipt, receipt_id)
    if not r or r.user_id != user.id:
        return RedirectResponse("/receipts", status_code=303)

    path = UPLOADS_DIR / r.stored_name
    if not path.exists():
        return RedirectResponse("/receipts", status_code=303)

    return FileResponse(
        path=str(path),
        filename=r.original_name,
        media_type=r.content_type
    )
