from fastapi import FastAPI

app = FastAPI(
    title="One-Shot API",
    description="An API for generating RPG one-shot stories using AI agents",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the One-Shot API"} 