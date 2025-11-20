"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.database import init_db
from app.routers import admin, products, upload, webhooks


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    application = FastAPI(title=settings.app_name)

    application.include_router(upload.router)
    application.include_router(products.router)
    application.include_router(webhooks.router)
    application.include_router(admin.router)

    application.mount("/static", StaticFiles(directory="static"), name="static")
    # Serve raw HTML templates for simple navigation/testing.
    application.mount("/templates", StaticFiles(directory="templates", html=True), name="templates")
    application.state.templates = Jinja2Templates(directory="templates")

    @application.on_event("startup")
    def _startup() -> None:
        init_db()

    @application.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/templates/upload.html")

    return application


app = create_app()
