from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from one_shot_api.api.health import router as health_router
from one_shot_api.config import get_settings
from one_shot_api.core.error_handlers import (
    generic_error_handler,
    one_shot_api_error_handler,
)
from one_shot_api.core.exceptions import OneShotAPIError
from one_shot_api.core.logging import setup_logging

settings = get_settings()

# Setup logging
log_file = Path("logs/one_shot_api.log")
log_file.parent.mkdir(exist_ok=True)
logger = setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=log_file,
    json_format=settings.LOG_JSON_FORMAT,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API for generating RPG one-shot stories using AI agents",
    version="0.1.0",
    openapi_url="/openapi.json",
)

# Add logger to app state
app.logger = logger

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
app.add_exception_handler(OneShotAPIError, one_shot_api_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Include routers
app.include_router(
    health_router, prefix=f"{settings.API_V1_STR}/health", tags=["health"]
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}
