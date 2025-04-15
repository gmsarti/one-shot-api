import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from one_shot_api.api.routes.story import generate_story, get_story
from one_shot_api.models.database import Story
from one_shot_api.models.story import StoryRequest, StoryResponse

# Constants for HTTP status codes
HTTP_STATUS_INTERNAL_ERROR = 500
HTTP_STATUS_NOT_FOUND = 404


@pytest.fixture
def mock_db() -> Session:
    return MagicMock(spec=Session)


@pytest.fixture
def mock_story() -> Story:
    return Story(
        id=1,
        title="Test Story",
        summary="A test story summary",
        plot_points=json.dumps(["Point 1", "Point 2"]),
        characters=json.dumps(["Character 1", "Character 2"]),
        locations=json.dumps(["Location 1", "Location 2"]),
        items=json.dumps(["Item 1", "Item 2"]),
        estimated_duration="120 minutes",
    )


@pytest.fixture
def story_request() -> StoryRequest:
    return StoryRequest(
        rpg_system="D&D 5e",
        length="medium",
        theme="fantasy",
        player_count=4,
        complexity=3,
    )


@pytest.mark.asyncio
async def test_generate_story_success(
    mock_db: Session, story_request: StoryRequest, mock_story: Story
) -> None:
    with (
        patch("one_shot_api.api.routes.story.StoryGenerator") as mock_generator,
        patch("one_shot_api.api.routes.story.settings") as mock_settings,
    ):
        # Setup mock
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_generator_instance = mock_generator.return_value
        mock_generator_instance.generate_story = AsyncMock(return_value=mock_story)

        # Call the endpoint
        response = await generate_story(story_request, mock_db)

        # Verify response
        assert isinstance(response, StoryResponse)
        assert response.title == "Test Story"
        assert response.summary == "A test story summary"
        assert response.plot_points == ["Point 1", "Point 2"]
        assert response.characters == ["Character 1", "Character 2"]
        assert response.locations == ["Location 1", "Location 2"]
        assert response.items == ["Item 1", "Item 2"]
        assert response.estimated_duration == "120 minutes"


@pytest.mark.asyncio
async def test_generate_story_no_api_key(mock_db):
    with patch("one_shot_api.api.routes.story.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = None
        story_request = StoryRequest(
            rpg_system="D&D 5e",
            length="medium",
            theme="fantasy",
            player_count=4,
            complexity=3,
        )

        with pytest.raises(HTTPException) as exc_info:
            await generate_story(story_request, mock_db)

        assert exc_info.value.status_code == HTTP_STATUS_INTERNAL_ERROR
        assert exc_info.value.detail == "OpenAI API key not configured"


@pytest.mark.asyncio
async def test_generate_story_failure(mock_db):
    with (
        patch("one_shot_api.api.routes.story.settings") as mock_settings,
        patch("one_shot_api.api.routes.story.StoryGenerator") as mock_generator,
    ):
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_generator_instance = mock_generator.return_value
        mock_generator_instance.generate_story = AsyncMock(
            side_effect=Exception("Test error")
        )

        story_request = StoryRequest(
            rpg_system="D&D 5e",
            length="medium",
            theme="fantasy",
            player_count=4,
            complexity=3,
        )

        with pytest.raises(HTTPException) as exc_info:
            await generate_story(story_request, mock_db)

        assert exc_info.value.status_code == HTTP_STATUS_INTERNAL_ERROR
        assert "Failed to generate story" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_story_success(mock_db: Session, mock_story: Story) -> None:
    # Setup mock
    mock_db.query.return_value.filter.return_value.first.return_value = mock_story

    # Call the endpoint
    response = await get_story(1, mock_db)

    # Verify response
    assert isinstance(response, StoryResponse)
    assert response.title == "Test Story"
    assert response.summary == "A test story summary"
    assert response.plot_points == ["Point 1", "Point 2"]
    assert response.characters == ["Character 1", "Character 2"]
    assert response.locations == ["Location 1", "Location 2"]
    assert response.items == ["Item 1", "Item 2"]
    assert response.estimated_duration == "120 minutes"


@pytest.mark.asyncio
async def test_get_story_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_story(1, mock_db)

    assert exc_info.value.status_code == HTTP_STATUS_NOT_FOUND
    assert exc_info.value.detail == "Story not found"


@pytest.mark.asyncio
async def test_get_story_database_error(mock_db):
    # Setup mock to raise an exception
    mock_db.query.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await get_story(1, mock_db)

    assert exc_info.value.status_code == HTTP_STATUS_INTERNAL_ERROR
    assert "Database error" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_story_invalid_json(mock_db, mock_story):
    # Setup mock to return a story with invalid JSON
    mock_story.plot_points = "invalid json"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_story

    with pytest.raises(HTTPException) as exc_info:
        await get_story(1, mock_db)

    assert exc_info.value.status_code == HTTP_STATUS_INTERNAL_ERROR
    assert "Invalid JSON data" in exc_info.value.detail
