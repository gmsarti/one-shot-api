from .api.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("one_shot_api.api.main:app", host="0.0.0.0", port=8001, reload=True) 