from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, test, players, crowd, auth

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
    return {
        "status": "success",
        "message": "Backend is running!"
    }

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(test.router)
app.include_router(players.router)
app.include_router(crowd.router)
