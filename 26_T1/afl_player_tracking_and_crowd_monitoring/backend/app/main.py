from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.routes import health, test, players, crowd, auth
from app import config

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Orion Backend API",
    description="API for player tracking and crowd monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint hit")
    return {
        "status": "success",
        "message": "Backend is running!"
    }

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(test.router)
app.include_router(players.router)
app.include_router(crowd.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "details": str(exc) if config.DEBUG else "Something went wrong"
        },
    )