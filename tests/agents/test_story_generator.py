import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage
from sqlalchemy.orm import Session

from one_shot_api.agents.story_generator import StoryGenerator
from one_shot_api.models.database import Keyword, Story
from one_shot_api.models.story import StoryRequest, StoryResponse

# Constants for test data
DB_STORY_KEYWORDS_COUNT = 3  # Story + 2 keywords

# Constants for magic numbers
HTTP_STATUS_OK = 200
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_INTERNAL_ERROR = 500
STORY_KEYWORDS_COUNT = 3


@pytest.fixture
def mock_llm():
    return MagicMock()


@pytest.fixture
def mock_prompt():
    return MagicMock()


@pytest.fixture
def mock_parser():
    return MagicMock()


@pytest.fixture
def generator(mock_llm, mock_prompt, mock_parser):
    with (
        patch("one_shot_api.agents.story_generator.ChatOpenAI", return_value=mock_llm),
        patch(
            "one_shot_api.agents.story_generator.ChatPromptTemplate",
            return_value=mock_prompt,
        ),
        patch(
            "one_shot_api.agents.story_generator.PydanticOutputParser",
            return_value=mock_parser,
        ),
    ):
        return StoryGenerator("test-api-key")


@pytest.fixture
def mock_db() -> Session:
    return MagicMock(spec=Session)


@pytest.fixture
def story_request() -> StoryRequest:
    return StoryRequest(
        rpg_system="D&D 5e",
        length="medium",
        theme="fantasy",
        player_count=4,
        complexity=3,
    )


@pytest.fixture
def story_response() -> StoryResponse:
    return StoryResponse(
        title="Test Story",
        summary="A test story summary",
        plot_points=["Point 1", "Point 2"],
        characters=["Character 1", "Character 2"],
        locations=["Location 1", "Location 2"],
        items=["Item 1", "Item 2"],
        estimated_duration="120 minutes",
    )


@pytest.mark.asyncio
async def test_extract_keywords_invalid_json(story_response: StoryResponse) -> None:
    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response
        mock_response = AIMessage(content="invalid json")
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == []
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_extract_keywords_array_like_content(
    story_response: StoryResponse,
) -> None:
    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response
        mock_response = AIMessage(
            content="[keyword1, keyword2]"
        )  # Not valid JSON but array-like
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == []  # Should return empty list for invalid JSON
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_extract_keywords_non_list_json(story_response: StoryResponse) -> None:
    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response
        mock_response = AIMessage(
            content='{"keywords": ["keyword1", "keyword2"]}'
        )  # Valid JSON but not a list
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == []  # Should return empty list for non-list JSON
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_save_to_database(
    story_response: StoryResponse, story_request: StoryRequest, mock_db: Session
) -> None:
    # Setup mock
    mock_query = MagicMock()
    mock_filter = MagicMock()

    mock_db.query = MagicMock(return_value=mock_query)
    mock_query.filter = MagicMock(return_value=mock_filter)
    mock_filter.first = MagicMock(return_value=None)

    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    # Create generator
    generator = StoryGenerator("test-api-key")

    # Call method
    keywords = ["keyword1", "keyword2"]
    result = await generator.save_to_database(
        story_response, story_request, keywords, mock_db
    )

    # Verify database calls
    assert mock_db.add.call_count >= 1  # At least one call for the story
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    # Verify result
    assert isinstance(result, Story)
    assert result.title == story_response.title
    assert result.summary == story_response.summary
    assert json.loads(result.plot_points) == story_response.plot_points
    assert json.loads(result.characters) == story_response.characters
    assert json.loads(result.locations) == story_response.locations
    assert json.loads(result.items) == story_response.items
    assert result.estimated_duration == story_response.estimated_duration


def test_parse_story_parts(generator):
    test_cases = [
        ("Title: Test\nContent: Story", ["Title: Test", "Content: Story"]),
        ("Title: Test\n\nContent: Story", ["Title: Test", "Content: Story"]),
        (
            "Title: Test\nContent: Story\nExtra: Info",
            ["Title: Test", "Content: Story", "Extra: Info"],
        ),
    ]

    for input_text, expected in test_cases:
        result = generator.parse_story_parts(input_text)
        assert result == expected


@pytest.mark.asyncio
async def test_parse_story_parts_empty_input(generator):
    result = generator.parse_story_parts("")
    assert result == []


@pytest.mark.asyncio
async def test_parse_story_parts_single_line(generator):
    result = generator.parse_story_parts("Single line story")
    assert result == ["Single line story"]


@pytest.mark.asyncio
async def test_parse_story_parts_multiple_lines(generator):
    story_text = """
    Line 1
    Line 2

    Line 3
    """
    result = generator.parse_story_parts(story_text)
    assert result == ["Line 1", "Line 2", "Line 3"]


@pytest.mark.asyncio
async def test_parse_story_parts_with_whitespace(generator):
    story_text = "   Line 1   \n   Line 2   \n   \n   Line 3   "
    result = generator.parse_story_parts(story_text)
    assert result == ["Line 1", "Line 2", "Line 3"]


@pytest.mark.asyncio
async def test_extract_keywords_empty_story(story_response: StoryResponse) -> None:
    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response
        mock_response = AIMessage(content="[]")
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == []
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_extract_keywords_with_special_characters(
    story_response: StoryResponse,
) -> None:
    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response
        mock_response = AIMessage(content='["keyword-1", "keyword_2", "keyword 3"]')
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == ["keyword-1", "keyword_2", "keyword 3"]
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_extract_keywords_with_numbers(story_response: StoryResponse) -> None:
    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response
        mock_response = AIMessage(content='["keyword1", "keyword2", "123"]')
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == ["keyword1", "keyword2", "123"]
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_extract_keywords_success(story_response: StoryResponse) -> None:
    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response with valid JSON array
        mock_response = AIMessage(content='["adventure", "dragon", "treasure"]')
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == ["adventure", "dragon", "treasure"]
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_generate_story_with_custom_theme(generator, mock_db) -> None:
    # Create a story request with custom theme
    story_request = StoryRequest(
        rpg_system="D&D 5e",
        length="medium",
        theme="custom",
        custom_theme="A steampunk adventure in a floating city",
        player_count=4,
        complexity=3,
    )

    # Create a mock story response
    mock_story_response = StoryResponse(
        title="The Clockwork Conspiracy",
        summary="A thrilling steampunk adventure in the floating city of Aetheria",
        plot_points=[
            "The party discovers a plot to sabotage the city's levitation engines"
        ],
        characters=["Captain Amelia Windwhistle", "Professor Reginald Cogsworth"],
        locations=["The Floating City of Aetheria", "The Clockwork District"],
        items=["Steam-powered grappling hook", "Aether crystal"],
        estimated_duration="120 minutes",
    )

    # Create an awaitable mock chain
    class AsyncChainMock:
        def __init__(self, response):
            self.response = response
            self.ainvoke = AsyncMock(return_value=response)

        def __or__(self, other):
            return self

    # Create the mock chain
    mock_chain = AsyncChainMock(mock_story_response)

    # Mock the prompt template
    mock_prompt = MagicMock()
    mock_prompt.__or__.return_value = mock_chain

    # Mock the LLM
    mock_llm = AsyncMock()
    mock_llm.__or__.return_value = mock_chain

    # Mock the parser
    mock_parser = AsyncMock()
    mock_parser.__or__.return_value = mock_chain

    # Set up the mocked components
    with patch(
        "one_shot_api.agents.story_generator.ChatPromptTemplate"
    ) as prompt_class:
        prompt_class.from_messages.return_value = mock_prompt
        generator.llm = mock_llm
        generator.parser = mock_parser

        # Mock the extract_keywords method
        mock_keywords = ["steampunk", "adventure", "city", "conspiracy"]
        with patch.object(
            generator, "extract_keywords", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_keywords

            # Mock the save_to_database method
            mock_db_story = Story(
                id=1,
                title=mock_story_response.title,
                summary=mock_story_response.summary,
                plot_points=json.dumps(mock_story_response.plot_points),
                characters=json.dumps(mock_story_response.characters),
                locations=json.dumps(mock_story_response.locations),
                items=json.dumps(mock_story_response.items),
                estimated_duration=mock_story_response.estimated_duration,
                rpg_system=story_request.rpg_system,
                theme=story_request.theme,
                player_count=story_request.player_count,
                complexity=story_request.complexity,
            )
            with patch.object(
                generator, "save_to_database", new_callable=AsyncMock
            ) as mock_save:
                mock_save.return_value = mock_db_story

                # Generate the story
                result = await generator.generate_story(story_request, mock_db)

                # Verify the story was generated with custom theme
                assert result.title == mock_story_response.title
                assert result.summary == mock_story_response.summary
                assert json.loads(result.plot_points) == mock_story_response.plot_points
                assert json.loads(result.characters) == mock_story_response.characters
                assert json.loads(result.locations) == mock_story_response.locations
                assert json.loads(result.items) == mock_story_response.items
                assert (
                    result.estimated_duration == mock_story_response.estimated_duration
                )
                assert result.rpg_system == story_request.rpg_system
                assert result.theme == story_request.theme
                assert result.player_count == story_request.player_count
                assert result.complexity == story_request.complexity

                # Verify the chain was called with the correct theme
                mock_chain.ainvoke.assert_called_once_with(
                    {
                        "length": story_request.length,
                        "rpg_system": story_request.rpg_system,
                        "theme": story_request.theme,
                        "player_count": story_request.player_count,
                        "complexity": story_request.complexity,
                        "custom_theme_text": "- Custom Theme: A steampunk adventure in a floating city",
                    }
                )

                # Verify keywords were extracted
                mock_extract.assert_called_once_with(mock_story_response)

                # Verify the story was saved to the database
                mock_save.assert_called_once_with(
                    mock_story_response, story_request, mock_keywords, mock_db
                )


@pytest.mark.asyncio
async def test_generate_story_simple(generator, mock_db) -> None:
    # Create a basic story request
    story_request = StoryRequest(
        rpg_system="D&D 5e",
        length="short",
        theme="fantasy",
        player_count=4,
        complexity=1,
    )

    # Mock a simple story response
    mock_story_response = StoryResponse(
        title="Test Adventure",
        summary="A simple test adventure",
        plot_points=["Point 1", "Point 2", "Point 3"],
        characters=["Hero", "Villain", "Ally"],
        locations=["Castle", "Forest", "Cave"],
        items=["Magic Sword", "Ancient Map", "Healing Potion"],
        estimated_duration="60 minutes",
    )

    # Create a simple async mock that returns our response
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = mock_story_response

    # Replace the chain components with our mock
    generator.llm = AsyncMock()
    generator.parser = AsyncMock()
    generator.llm.__or__.return_value = mock_chain
    generator.parser.__or__.return_value = mock_chain

    # Mock the database operations
    mock_db_story = Story(
        id=1,
        title=mock_story_response.title,
        summary=mock_story_response.summary,
        plot_points=json.dumps(mock_story_response.plot_points),
        characters=json.dumps(mock_story_response.characters),
        locations=json.dumps(mock_story_response.locations),
        items=json.dumps(mock_story_response.items),
        estimated_duration=mock_story_response.estimated_duration,
        rpg_system=story_request.rpg_system,
        theme=story_request.theme,
        player_count=story_request.player_count,
        complexity=story_request.complexity,
    )

    # Mock extract_keywords
    mock_keywords = ["fantasy", "adventure", "quest"]
    with patch.object(
        generator, "extract_keywords", new_callable=AsyncMock
    ) as mock_extract:
        mock_extract.return_value = mock_keywords

        # Mock save_to_database
        with patch.object(
            generator, "save_to_database", new_callable=AsyncMock
        ) as mock_save:
            mock_save.return_value = mock_db_story

            # Generate the story
            result = await generator.generate_story(story_request, mock_db)

            # Basic assertions
            assert result is not None
            assert result.title == mock_story_response.title
            assert json.loads(result.plot_points) == mock_story_response.plot_points
            assert json.loads(result.characters) == mock_story_response.characters
            assert json.loads(result.locations) == mock_story_response.locations
            assert json.loads(result.items) == mock_story_response.items
            assert result.estimated_duration == mock_story_response.estimated_duration
            assert result.rpg_system == story_request.rpg_system
            assert result.theme == story_request.theme
            assert result.player_count == story_request.player_count
            assert result.complexity == story_request.complexity


@pytest.mark.asyncio
async def test_save_story_to_database(generator, mock_db) -> None:
    # Create a story response to save
    story_response = StoryResponse(
        title="Test Adventure",
        summary="A simple test adventure",
        plot_points=["Point 1", "Point 2", "Point 3"],
        characters=["Hero", "Villain", "Ally"],
        locations=["Castle", "Forest", "Cave"],
        items=["Magic Sword", "Ancient Map", "Healing Potion"],
        estimated_duration="60 minutes",
    )

    # Create a story request
    story_request = StoryRequest(
        rpg_system="D&D 5e",
        length="short",
        theme="fantasy",
        player_count=4,
        complexity=1,
    )

    # Mock keywords
    keywords = ["fantasy", "adventure", "quest"]

    # Create mock database session
    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    mock_db.flush = MagicMock()

    # Create existing keyword for "fantasy"
    existing_keyword = Keyword(id=1, keyword="fantasy")

    # Set up the query chain for existing keywords
    def mock_query_side_effect(model):
        mock_query = MagicMock()

        def mock_filter_side_effect(condition):
            mock_filter = MagicMock()
            if isinstance(model, type(Keyword)) and "fantasy" in str(condition):
                mock_filter.first = MagicMock(return_value=existing_keyword)
            else:
                mock_filter.first = MagicMock(return_value=None)
            return mock_filter

        mock_query.filter = MagicMock(side_effect=mock_filter_side_effect)
        return mock_query

    mock_db.query = MagicMock(side_effect=mock_query_side_effect)

    # Create a mock story with a keywords list
    mock_story = Story(
        title=story_response.title,
        summary=story_response.summary,
        plot_points=json.dumps(story_response.plot_points),
        characters=json.dumps(story_response.characters),
        locations=json.dumps(story_response.locations),
        items=json.dumps(story_response.items),
        estimated_duration=story_response.estimated_duration,
        rpg_system=story_request.rpg_system,
        theme=story_request.theme,
        player_count=story_request.player_count,
        complexity=story_request.complexity,
    )
    mock_story.keywords = []

    # Track story and keyword additions
    added_objects = []

    def mock_add(obj):
        if isinstance(obj, Story):
            added_objects.append(obj)
            return mock_story
        if isinstance(obj, Keyword):
            # Only add if it's not the existing keyword
            if obj.keyword != "fantasy":
                added_objects.append(obj)
        return obj

    mock_db.add.side_effect = mock_add

    # Call save_to_database
    result = await generator.save_to_database(
        story_response, story_request, keywords, mock_db
    )

    # Verify database operations
    assert mock_db.add.call_count == len(keywords) + 1  # Story + keywords
    assert len(added_objects) == len(keywords)  # Each keyword should be added
    assert all(
        k.keyword in keywords for k in added_objects if isinstance(k, Keyword)
    )  # All keywords should be present
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    # Verify the story was saved correctly
    assert result.title == story_response.title
    assert result.summary == story_response.summary
    assert json.loads(result.plot_points) == story_response.plot_points
    assert json.loads(result.characters) == story_response.characters
    assert json.loads(result.locations) == story_response.locations
    assert json.loads(result.items) == story_response.items
    assert result.estimated_duration == story_response.estimated_duration
    assert result.rpg_system == story_request.rpg_system
    assert result.theme == story_request.theme
    assert result.player_count == story_request.player_count
    assert result.complexity == story_request.complexity


@pytest.mark.asyncio
async def test_generate_story():
    """Test the entire story generation pipeline."""
    # Create a mock story response
    story_response = StoryResponse(
        title="The Floating City",
        summary="In a world of steam and gears, a group of adventurers must navigate the floating city of Aetheria to uncover a conspiracy that threatens to bring the entire city crashing down.",
        plot_points=[
            "The party is hired to investigate strange power fluctuations in the city's core",
            "They discover a group of rebels trying to sabotage the city's levitation system",
            "The party must choose between helping the rebels or stopping them",
            "A final confrontation in the city's control room determines the fate of Aetheria",
        ],
        characters=[
            "Captain Amelia - A veteran airship pilot",
            "Professor Thaddeus - The city's chief engineer",
            "Luna - A young street urchin with a knack for mechanics",
            "The Iron Baron - The city's mysterious ruler",
        ],
        locations=[
            "The Floating Market - A bustling bazaar suspended between buildings",
            "The Steamworks - The city's industrial heart",
            "The Aether Core - The source of the city's levitation",
            "The Baron's Tower - The highest point in the city",
        ],
        items=[
            "Aether Compass - Points to sources of magical energy",
            "Steam-powered Grappling Hook - For navigating the city's heights",
            "Rebel Manifesto - Outlines the group's grievances",
            "Core Stabilizer - A device that can control the city's levitation",
        ],
        estimated_duration="3-4 hours",
    )

    # Create a mock database session
    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    # Create a story generator with our mocks
    generator = StoryGenerator("test-api-key")

    # Create an awaitable mock chain
    class AsyncChainMock:
        def __init__(self, response):
            self.response = response
            self.ainvoke = AsyncMock(return_value=response)

        def __or__(self, other):
            return self

    # Create the mock chain
    mock_chain = AsyncChainMock(story_response)

    # Mock the prompt template
    mock_prompt = MagicMock()
    mock_prompt.__or__.return_value = mock_chain

    # Mock the LLM
    mock_llm = AsyncMock()
    mock_llm.__or__.return_value = mock_chain

    # Mock the parser
    mock_parser = AsyncMock()
    mock_parser.__or__.return_value = mock_chain

    # Set up the mocked components
    with patch(
        "one_shot_api.agents.story_generator.ChatPromptTemplate"
    ) as prompt_class:
        prompt_class.from_messages.return_value = mock_prompt
        generator.llm = mock_llm
        generator.parser = mock_parser

        # Mock the extract_keywords method
        mock_keywords = ["steampunk", "adventure", "city", "conspiracy"]
        with patch.object(
            generator, "extract_keywords", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_keywords

            # Mock the save_to_database method
            mock_db_story = Story(
                id=1,
                title=story_response.title,
                summary=story_response.summary,
                plot_points=json.dumps(story_response.plot_points),
                characters=json.dumps(story_response.characters),
                locations=json.dumps(story_response.locations),
                items=json.dumps(story_response.items),
                estimated_duration=story_response.estimated_duration,
                rpg_system="D&D 5e",
                theme="custom",
                player_count=4,
                complexity=3,
            )
            with patch.object(
                generator, "save_to_database", new_callable=AsyncMock
            ) as mock_save:
                mock_save.return_value = mock_db_story

                # Create a story request
                story_request = StoryRequest(
                    rpg_system="D&D 5e",
                    length="medium",
                    theme="custom",
                    custom_theme="A steampunk adventure in a floating city",
                    player_count=4,
                    complexity=3,
                )

                # Generate the story
                result = await generator.generate_story(story_request, mock_db)

                # Verify the result
                assert result is not None
                assert result.title == story_response.title
                assert result.summary == story_response.summary
                assert json.loads(result.plot_points) == story_response.plot_points
                assert json.loads(result.characters) == story_response.characters
                assert json.loads(result.locations) == story_response.locations
                assert json.loads(result.items) == story_response.items
                assert result.estimated_duration == story_response.estimated_duration

                # Verify the chain was called with the correct theme
                mock_chain.ainvoke.assert_called_once_with(
                    {
                        "length": story_request.length,
                        "rpg_system": story_request.rpg_system,
                        "theme": story_request.theme,
                        "player_count": story_request.player_count,
                        "complexity": story_request.complexity,
                        "custom_theme_text": "- Custom Theme: A steampunk adventure in a floating city",
                    }
                )

                # Verify keywords were extracted
                mock_extract.assert_called_once_with(story_response)

                # Verify the story was saved to the database
                mock_save.assert_called_once_with(
                    story_response, story_request, mock_keywords, mock_db
                )


@pytest.mark.asyncio
async def test_extract_keywords_success_with_special_chars():
    """Test keyword extraction with special characters in the response."""
    story_response = StoryResponse(
        title="Test Story",
        summary="A test story summary",
        plot_points=["Point 1", "Point 2"],
        characters=["Character 1", "Character 2"],
        locations=["Location 1", "Location 2"],
        items=["Item 1", "Item 2"],
        estimated_duration="120 minutes",
    )

    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response with special characters
        mock_response = AIMessage(
            content='["fantasy-rpg", "sci_fi", "space opera", "cyber/punk"]'
        )
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == ["fantasy-rpg", "sci_fi", "space opera", "cyber/punk"]
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_extract_keywords_with_empty_response():
    """Test keyword extraction with an empty response."""
    story_response = StoryResponse(
        title="Test Story",
        summary="A test story summary",
        plot_points=["Point 1", "Point 2"],
        characters=["Character 1", "Character 2"],
        locations=["Location 1", "Location 2"],
        items=["Item 1", "Item 2"],
        estimated_duration="120 minutes",
    )

    with patch("one_shot_api.agents.story_generator.ChatPromptTemplate") as mock_prompt:
        # Setup mock response with empty content
        mock_response = AIMessage(content="")
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.from_messages.return_value.__or__.return_value = mock_chain

        # Create generator and test
        generator = StoryGenerator("test-api-key")
        keywords = await generator.extract_keywords(story_response)

        # Assertions
        assert keywords == []
        mock_chain.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_save_to_database_with_existing_keywords():
    """Test saving a story to the database with existing keywords."""
    # Create test data
    story_response = StoryResponse(
        title="Test Story",
        summary="A test story summary",
        plot_points=["Point 1", "Point 2"],
        characters=["Character 1", "Character 2"],
        locations=["Location 1", "Location 2"],
        items=["Item 1", "Item 2"],
        estimated_duration="120 minutes",
    )

    story_request = StoryRequest(
        rpg_system="D&D 5e",
        length="medium",
        theme="fantasy",
        player_count=4,
        complexity=3,
    )

    # Create mock database session
    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    mock_db.flush = MagicMock()

    # Create existing keyword for "fantasy"
    existing_keyword = Keyword(id=1, keyword="fantasy")

    # Set up the query chain for existing keywords
    def mock_query_side_effect(model):
        mock_query = MagicMock()

        def mock_filter_side_effect(condition):
            mock_filter = MagicMock()
            if isinstance(model, type(Keyword)) and "fantasy" in str(condition):
                mock_filter.first = MagicMock(return_value=existing_keyword)
            else:
                mock_filter.first = MagicMock(return_value=None)
            return mock_filter

        mock_query.filter = MagicMock(side_effect=mock_filter_side_effect)
        return mock_query

    mock_db.query = MagicMock(side_effect=mock_query_side_effect)

    # Create a mock story with a keywords list
    mock_story = Story(
        title=story_response.title,
        summary=story_response.summary,
        plot_points=json.dumps(story_response.plot_points),
        characters=json.dumps(story_response.characters),
        locations=json.dumps(story_response.locations),
        items=json.dumps(story_response.items),
        estimated_duration=story_response.estimated_duration,
        rpg_system=story_request.rpg_system,
        theme=story_request.theme,
        player_count=story_request.player_count,
        complexity=story_request.complexity,
    )
    mock_story.keywords = []

    # Track story and keyword additions
    added_objects = []

    def mock_add(obj):
        if isinstance(obj, Story):
            added_objects.append(obj)
            return mock_story
        if isinstance(obj, Keyword):
            # Only add if it's not the existing keyword
            if obj.keyword != "fantasy":
                added_objects.append(obj)
        return obj

    mock_db.add.side_effect = mock_add

    # Create generator
    generator = StoryGenerator("test-api-key")

    # Call method with mixed new and existing keywords
    keywords = ["fantasy", "adventure"]
    result = await generator.save_to_database(
        story_response, story_request, keywords, mock_db
    )

    # Verify database calls
    assert (
        mock_db.add.call_count == 3
    )  # One for story, one for new keyword, one for association table
    assert (
        len([obj for obj in added_objects if isinstance(obj, Story)]) == 1
    )  # One story added
    assert (
        len([obj for obj in added_objects if isinstance(obj, Keyword)]) == 1
    )  # One new keyword added
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    # Verify story attributes
    assert result.title == story_response.title
    assert result.summary == story_response.summary
    assert json.loads(result.plot_points) == story_response.plot_points
    assert json.loads(result.characters) == story_response.characters
    assert json.loads(result.locations) == story_response.locations
    assert json.loads(result.items) == story_response.items
    assert result.estimated_duration == story_response.estimated_duration
    assert result.rpg_system == story_request.rpg_system
    assert result.theme == story_request.theme
    assert result.player_count == story_request.player_count
    assert result.complexity == story_request.complexity

    # Verify database operations were called
    assert mock_db.add.call_count == len(keywords) + 1  # Story + keywords
    assert len(added_objects) == len(keywords)  # Each keyword should be added
    assert all(
        k.keyword in keywords for k in added_objects if isinstance(k, Keyword)
    )  # All keywords should be present
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_save_to_database_with_database_error():
    """Test handling of database errors when saving a story."""
    # Create test data
    story_response = StoryResponse(
        title="Test Story",
        summary="A test story summary",
        plot_points=["Point 1", "Point 2"],
        characters=["Character 1", "Character 2"],
        locations=["Location 1", "Location 2"],
        items=["Item 1", "Item 2"],
        estimated_duration="120 minutes",
    )

    story_request = StoryRequest(
        rpg_system="D&D 5e",
        length="medium",
        theme="fantasy",
        player_count=4,
        complexity=3,
    )

    # Create mock database session that raises an error
    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock(side_effect=Exception("Database error"))

    # Create generator
    generator = StoryGenerator("test-api-key")

    # Call method and expect an error
    keywords = ["fantasy", "adventure"]
    with pytest.raises(Exception, match="Database error"):
        await generator.save_to_database(
            story_response, story_request, keywords, mock_db
        )

    # Verify database calls
    mock_db.add.assert_called_once()
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called()


def test_parse_story_parts_with_empty_lines():
    """Test parsing story parts with empty lines."""
    generator = StoryGenerator("test-api-key")
    story_text = """

    Line 1

    Line 2

    Line 3

    """
    result = generator.parse_story_parts(story_text)
    assert result == ["Line 1", "Line 2", "Line 3"]


def test_parse_story_parts_with_special_chars():
    """Test parsing story parts with special characters."""
    generator = StoryGenerator("test-api-key")
    story_text = """
    Line 1!@#$%^&*()
    Line 2-_=+[]{};:'".<>?/
    Line 3\t\r\n
    """
    result = generator.parse_story_parts(story_text)
    assert result == ["Line 1!@#$%^&*()", "Line 2-_=+[]{};:'\".<>?/", "Line 3"]
