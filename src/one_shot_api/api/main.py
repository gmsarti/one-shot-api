from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import story
from ..utils.config import settings

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
app.include_router(story.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the One-Shot RPG Story Generator API",
        "version": "0.1.0",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 