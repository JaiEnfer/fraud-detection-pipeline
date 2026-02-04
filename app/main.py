from fastapi import FastAPI

from app.api.routes import router as api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
    app.include_router(api_router)
    return app


app = create_app()
