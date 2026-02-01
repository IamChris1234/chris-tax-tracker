from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import csv
import io

from app.auth import get_current_user_id
from app.db import get_db
from app.models import Transaction

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

TX_TYPES = ["T4", "T5", "Commission", "Rental"]
DIRECTIONS = ["expense", "income"]


def parse_date_guess(s: str):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_money(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s.replace("$", "").replace(",", ""))
    except ValueError:
        return None


def read_csv_rows(raw_text: str, max_rows: int = 20):
    reader = csv.DictReader(io.StringIO(raw_text))
    fieldnames = reader.fieldnames or []
    rows = []
    for i, row in enumerate(reader):
        if i >= max_rows:
            break
        rows.append(row)
    return fieldnames, rows


@router.get("/import/rr60")
def rr60_import_page(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        "import_rr60.html",
        {
            "request": request,
            "stage": "upload",
            "tx_types": TX_TYPES,
            "directions": DIRECTIONS,
        }
    )


@router.post("/import/rr60/preview")
def rr60_preview(
    request: Request,
    csv_file: UploadFile = File(...),
):
    user_id = get_current_user_id(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    raw = csv_file.file.read().decode("utf-8", errors="ignore")
    fieldnames, rows = read_csv_rows(raw, max_rows=20)

    # store raw in a hidden form field (simple for now).
    # Later we’ll store it server-side in Redis/S3.
    return templates.TemplateResponse(
        "import_rr60.html",
        {
            "request": request,
            "stage": "map",
            "raw_csv": raw,
            "columns": fieldnames,
            "preview_rows": rows,
            "tx_types": TX_TYPES,
            "directions": DIRECTIONS,
        }
    )


@router.post("/import/rr60/import")
def rr60_import(
    request: Request,
    raw_csv: str = Form(...),

    col_date: str = Form(...),
    col_vendor: str = Form(...),
    col_amount: str = Form(...),

    col_tax: str = Form(""),
    col_description: str = Form(""),

    default_direction: str = Form("expense"),
    default_type: str = Form("Commission"),

    db: Session = next(get_db()),
):
    user_id = get_current_user_id(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    default_direction = "income" if default_direction == "income" else "expense"
    if default_type not in TX_TYPES:
        default_type = "Commission"

    reader = csv.DictReader(io.StringIO(raw_csv))
    created = 0
    skipped = 0

    for row in reader:
        d = parse_date_guess(row.get(col_date, ""))
        vendor = (row.get(col_vendor, "") or "").strip()
        amt = parse_money(row.get(col_amount, ""))

        if not d or not vendor or amt is None:
            skipped += 1
            continue

        tax_val = 0.0
        if col_tax:
            tax_guess = parse_money(row.get(col_tax, ""))
            if tax_guess is not None:
                tax_val = tax_guess

        desc_val = ""
        if col_description:
            desc_val = (row.get(col_description, "") or "").strip()

        txn = Transaction(
            user_id=user_id,
            property_id=None,
            category_id=None,
            date=d,
            vendor=vendor,
            description=desc_val,
            amount=amt,
            tax=tax_val,
            type=default_type,
            direction=default_direction,
            notes="Imported from RR-60"
        )
        db.add(txn)
        created += 1

    db.commit()

    return templates.TemplateResponse(
        "import_rr60.html",
        {
            "request": request,
            "stage": "done",
            "created": created,
            "skipped": skipped,
            "tx_types": TX_TYPES,
            "directions": DIRECTIONS,
        }
    )
