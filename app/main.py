from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router

app = FastAPI()

# Sessions (login)
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-later",
)

# Static files (so /static/app.css works)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    # land users on the app
    return RedirectResponse("/dashboard", status_code=303)
