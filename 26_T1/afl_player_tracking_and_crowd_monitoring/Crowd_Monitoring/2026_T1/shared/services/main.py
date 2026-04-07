"""FastAPI entry point for the shared service layer."""

from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Crowd Monitoring Services",
    docs_url="/",
    redoc_url="/redoc",
)

app.include_router(router)