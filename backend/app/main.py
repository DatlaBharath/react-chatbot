import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app import models  # noqa: F401  (register tables on Base.metadata)
from app.controllers import health_controller, message_controller
from app.core.config import settings
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Base setup: create tables on boot. Swap for Alembic migrations when the schema grows.
    Base.metadata.create_all(bind=engine)
    yield


logging.basicConfig(level=settings.log_level.upper())

app = FastAPI(title=settings.app_name, lifespan=lifespan)

api = APIRouter(prefix="/api")
api.include_router(health_controller.router)
api.include_router(message_controller.router)
app.include_router(api)
