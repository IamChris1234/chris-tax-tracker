import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.export_routes import router as export_router
from app.routes.fuel_routes import router as fuel_router
from app.routes.txn_routes import router as txn_router
from app.routes.attachments_routes import router as attachments_router
from app.routes.rr60_import_routes import router as rr60_import_router

app = FastAPI()

# Sessions (needed for login cookies)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,      # cookie only over https (Render uses https)
    same_site="lax",
)

# Static files (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routes
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(export_router)
app.include_router(fuel_router)
app.include_router(txn_router)
app.include_router(attachments_router)
app.include_router(rr60_import_router)

# Root: send user into the app
@app.get("/")
def root():
    return RedirectResponse("/dashboard", status_code=303)
