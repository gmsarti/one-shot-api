from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from one_shot_api.utils.database import get_db

router = APIRouter()


@router.get("")
@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies both API and database connectivity."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
