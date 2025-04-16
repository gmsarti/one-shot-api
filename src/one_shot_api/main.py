from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from one_shot_api.api.health import router as health_router

app = FastAPI(
    title="One-Shot API",
    description="An API for generating RPG one-shot stories using AI agents",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the One-Shot API"}
