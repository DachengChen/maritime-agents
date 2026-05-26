from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import init_db
from app.routers.health import router as health_router
from app.routers.reports import router as reports_router
from app.routers.tasks import router as tasks_router
from app.services.scheduler import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler_service.start()
    try:
        yield
    finally:
        scheduler_service.stop()


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(reports_router)
