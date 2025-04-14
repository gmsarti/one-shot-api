import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...agents.story_generator import StoryGenerator
from ...models.database import Story
from ...models.story import StoryRequest, StoryResponse
from ...utils.config import settings
from ...utils.database import get_db

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/generate", response_model=StoryResponse)
async def generate_story(
    request: StoryRequest, db: Session = Depends(get_db)
) -> StoryResponse:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate story: {e!s}")


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int, db: Session = Depends(get_db)) -> StoryResponse:
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
