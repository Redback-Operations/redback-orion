from fastapi import FastAPI
from app.routes import health

app = FastAPI()

app.include_router(health.router)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}
