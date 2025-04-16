from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from one_shot_api.api.health import router as health_router
from one_shot_api.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API for generating RPG one-shot stories using AI agents",
    version="0.1.0",
    openapi_url="/openapi.json",
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
app.include_router(
    health_router, prefix=f"{settings.API_V1_STR}/health", tags=["health"]
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}
