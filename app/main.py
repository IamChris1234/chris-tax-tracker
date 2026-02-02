from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.export_routes import router as export_router
from app.routes.fuel_routes import router as fuel_router
from app.routes.txn_routes import router as txn_router
from app.routes.attachments_routes import router as attachments_router

app = FastAPI()

# Static files (CSS, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(txn_router)
app.include_router(fuel_router)
app.include_router(attachments_router)
app.include_router(export_router)
