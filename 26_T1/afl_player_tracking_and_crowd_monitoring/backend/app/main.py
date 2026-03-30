from fastapi import FastAPI
from app.routes import health, test, players, crowd

app = FastAPI(
    title="Project Orion Backend API",
    description="API for player tracking and crowd monitoring",
    version="1.0.0"
)

app.include_router(health.router)

@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "Backend is running!"
    }

app.include_router(test.router)
app.include_router(players.router)
app.include_router(crowd.router)