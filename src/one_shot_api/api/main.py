from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import story_router

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


@app.get("/health")  # type: ignore[misc]
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
