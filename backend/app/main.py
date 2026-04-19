from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.api.notifications import router as notifications_router
from app.api.portfolio import router as portfolio_router
from app.api.pipeline import router as pipeline_router
from app.services.scheduler import start_scheduler
from app.api.settings import router as settings_router
from app.api.portfolio_assets import router as portfolio_assets_router
from app.api.users import router as users_router

app = FastAPI(title="PortaAI API")

# Allow frontend to call backend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(notifications_router)
app.include_router(portfolio_router)
app.include_router(pipeline_router)
app.include_router(settings_router)
app.include_router(portfolio_assets_router)
app.include_router(users_router)

start_scheduler()
@app.get("/")
def root():
    return {"message": "PortaAI API is running"}