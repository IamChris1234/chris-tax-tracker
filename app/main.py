# app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.config import SESSION_SECRET
from app.db import Base, engine
from app.storage import ensure_storage

from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.txn_routes import router as txn_router
from app.routes.fuel_routes import router as fuel_router
from app.routes.attachments_routes import router as attachments_router
from app.routes.export_routes import router as export_router
from app.routes.rr60_import_routes import router as rr60_router

app = FastAPI()

# sessions
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# init DB + storage
Base.metadata.create_all(bind=engine)
ensure_storage()

# routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(txn_router)
app.include_router(fuel_router)
app.include_router(attachments_router)
app.include_router(export_router)
app.include_router(rr60_router)

@app.get("/")
def root():
    return RedirectResponse("/dashboard", status_code=303)
