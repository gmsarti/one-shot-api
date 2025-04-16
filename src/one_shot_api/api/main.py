import psutil
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from one_shot_api.utils.database import get_db

from .routes.story import router as story_router

app = FastAPI(
    title="One-Shot RPG Story Generator",
    description="An API for generating RPG one-shot stories using AI agents",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(story_router, prefix="/api/v1", tags=["stories"])


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to the One-Shot RPG Story Generator API.\nCreate a one-shot!",
        "version": "0.1.0",
    }


@app.exception_handler(Exception)  # type: ignore[misc]
async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)},
    )


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Get system metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": {"status": db_status},
        "system": {
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            },
        },
    }
