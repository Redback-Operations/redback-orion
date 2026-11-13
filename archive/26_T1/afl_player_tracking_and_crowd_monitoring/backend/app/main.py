import logging
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import (
    health,
    test,
    players,
    crowd,
    auth,
    upload,
    jobs,
)

from app.database import engine
from app.models import Base
from app import config


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=config.LOG_LEVEL,
    format=(
        "%(asctime)s - %(levelname)s - "
        "%(name)s - %(message)s"
    ),
)

logger = logging.getLogger(__name__)


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    if os.getenv("TESTING") != "true":

        if not getattr(
            app.state,
            "db_initialized",
            False,
        ):

            async with engine.begin() as conn:
                await conn.run_sync(
                    Base.metadata.create_all
                )

            app.state.db_initialized = True

            logger.info(
                "Database tables created/verified"
            )

    else:

        logger.info(
            "TESTING=true, skipping database table creation"
        )

    yield


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Project Orion Backend API",
    description=(
        "API for player tracking and "
        "crowd monitoring"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# CORS
# =========================================================

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8081",
]

# When deployed, Railway will receive:
#
# FRONTEND_URL=https://your-project.vercel.app

if (
    config.FRONTEND_URL
    and config.FRONTEND_URL
    not in allowed_origins
):
    allowed_origins.append(
        config.FRONTEND_URL
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):

    logger.exception(
        "Unhandled error while processing %s",
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "details": (
                str(exc)
                if config.DEBUG
                else "Something went wrong"
            ),
        },
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def read_root():

    logger.info(
        "Root endpoint hit"
    )

    return {
        "status": "success",
        "message": "Backend is running!",
    }


# =========================================================
# ROUTES
# =========================================================

app.include_router(
    health.router,
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    upload.router,
    tags=["Upload"],
)

app.include_router(
    jobs.router,
    tags=["Jobs"],
)

app.include_router(
    test.router,
)

app.include_router(
    players.router,
)

app.include_router(
    crowd.router,
)