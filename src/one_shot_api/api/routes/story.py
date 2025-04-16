import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ...agents.story_generator import StoryGenerator
from ...models.database import Story
from ...models.story import StoryRequest, StoryResponse
from ...utils.config import settings
from ...utils.database import get_db

router = APIRouter(tags=["stories"])


@router.post("/generate", response_model=StoryResponse)
async def generate_story(
    request: StoryRequest, db: Session = Depends(get_db)
) -> StoryResponse:
    """Generate a new RPG one-shot story based on the provided parameters.

    This endpoint creates a new story using the StoryGenerator agent and saves it
    to the database. The story is generated based on the provided RPG system,
    theme, player count, and complexity parameters.

    Args:
        request (StoryRequest): The story generation request containing parameters
        db (Session): Database session (automatically injected)

    Returns:
        StoryResponse: The generated story with all its components

    Raises:
        HTTPException: If OpenAI API key is not configured
        HTTPException: If there's a database error
        HTTPException: If there's an error in JSON processing
        HTTPException: If story generation fails
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        generator = StoryGenerator(settings.OPENAI_API_KEY)
        story = await generator.generate_story(request, db)

        # Convert database story to response model
        return StoryResponse(
            title=story.title,
            summary=story.summary,
            plot_points=json.loads(story.plot_points),
            characters=json.loads(story.characters),
            locations=json.loads(story.locations),
            items=json.loads(story.items),
            estimated_duration=story.estimated_duration,
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e!s}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON data: {e!s}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate story: {e!s}")


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int, db: Session = Depends(get_db)) -> StoryResponse:
    """Retrieve a previously generated story by its ID.

    This endpoint fetches a story from the database and returns it in the
    StoryResponse format. The story must exist in the database.

    Args:
        story_id (int): The ID of the story to retrieve
        db (Session): Database session (automatically injected)

    Returns:
        StoryResponse: The requested story with all its components

    Raises:
        HTTPException: If the story is not found
        HTTPException: If there's a database error
        HTTPException: If there's an error in JSON processing
        HTTPException: If story retrieval fails
    """
    try:
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")

        return StoryResponse(
            title=story.title,
            summary=story.summary,
            plot_points=json.loads(story.plot_points),
            characters=json.loads(story.characters),
            locations=json.loads(story.locations),
            items=json.loads(story.items),
            estimated_duration=story.estimated_duration,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e!s}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON data: {e!s}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get story: {e!s}")
