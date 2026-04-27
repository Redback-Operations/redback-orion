"""FastAPI entry point for the shared service layer."""

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

from .routes import router

app = FastAPI(
    title="Crowd Monitoring Services",
    docs_url="/",
    redoc_url="/redoc",
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return actual runtime errors as JSON instead of generic 500 pages."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "path": request.url.path,
        },
    )


app.include_router(router)
