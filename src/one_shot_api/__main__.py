import uvicorn

from .utils.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "one_shot_api.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
