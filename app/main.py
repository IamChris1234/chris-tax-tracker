from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router

app = FastAPI()

# REQUIRED for sessions
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-later",
)

# ROUTES
app.include_router(auth_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {"status": "ok"}
