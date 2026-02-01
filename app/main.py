from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from .config import SECRET_KEY, APP_NAME
from .db import engine, Base

from .routes.auth_routes import router as auth_router
from .routes.txn_routes import router as txn_router
from .routes.fuel_routes import router as fuel_router
from .routes.attachments_routes import router as attachments_router
from .routes.export_routes import router as export_router
from .routes.dashboard_routes import router as dashboard_router

app = FastAPI(title=APP_NAME)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# create tables on boot (simple mode)
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(txn_router)
app.include_router(fuel_router)
app.include_router(attachments_router)
app.include_router(export_router)
