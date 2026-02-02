# app/routes/attachments_routes.py

from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/attachments", response_class=HTMLResponse)
def attachments_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    # If you already have a template, you can render it here.
    # For now, keep it simple so the site works.
    return HTMLResponse(
        """
        <h1>Attachments</h1>
        <p>Logged in ✅</p>
        <form method="post" action="/attachments/upload" enctype="multipart/form-data">
          <input type="file" name="file" />
          <button type="submit">Upload</button>
        </form>
        <p><a href="/dashboard">Back to dashboard</a></p>
        """,
        status_code=200,
    )


@router.post("/attachments/upload")
async def upload_attachment(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    # Placeholder behavior (prevents 500s). We’ll wire storage later.
    # Just read the bytes so the request succeeds.
    _ = await file.read()
    return RedirectResponse("/attachments", status_code=303)
