import io
import csv
import zipfile
from datetime import datetime
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user
from ..models import Transaction, Receipt
from ..config import UPLOADS_DIR

router = APIRouter(prefix="/export")

@router.get("/transactions.csv")
def export_transactions_csv(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    items = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.date.asc()).all()

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["date", "vendor", "description", "amount", "type", "notes"])
    for t in items:
        w.writerow([t.date.isoformat(), t.vendor, t.description, float(t.amount), t.type, t.notes])

    data = buf.getvalue().encode("utf-8")
    filename = f"transactions_{datetime.utcnow().date().isoformat()}.csv"
    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.get("/receipts.zip")
def export_receipts_zip(
    request: Request,
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    # pull receipts and filter by uploaded_at month
    receipts = db.query(Receipt).filter(Receipt.user_id == user.id).all()
    targets = [r for r in receipts if r.uploaded_at.year == year and r.uploaded_at.month == month]

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for r in targets:
            path = UPLOADS_DIR / r.stored_name
            if path.exists():
                z.write(path, arcname=r.original_name)

    zip_buf.seek(0)
    filename = f"receipts_{year:04d}-{month:02d}.zip"
    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
