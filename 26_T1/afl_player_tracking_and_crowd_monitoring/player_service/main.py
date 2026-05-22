import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import config
from routes import tracking, path_trajectory, jersey_color, tackle, formation

app = FastAPI(
    title="AFL Player Tracking Service",
    description="Microservice for AFL player tracking, jersey colour, tackle detection and formation analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tracking.router,        tags=["Tracking"])
app.include_router(path_trajectory.router, tags=["Path Trajectory"])
app.include_router(jersey_color.router,    tags=["Jersey Colour"])
app.include_router(tackle.router,          tags=["Tackle Detection"])
app.include_router(formation.router,       tags=["Formation Analysis"])


@app.get("/outputs/{job_id}/{filename}")
async def download_nested(job_id: str, filename: str):
    file_path = config.OUTPUTS_DIR / job_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))


@app.get("/outputs/{filename}")
async def download_flat(filename: str):
    file_path = config.OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path))


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "AFL Player Tracking Service",
        "port": 8080,
        "endpoints": [
            "POST /tracking",
            "POST /path_trajectory",
            "POST /jersey_color",
            "POST /tackle",
            "POST /formation"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
