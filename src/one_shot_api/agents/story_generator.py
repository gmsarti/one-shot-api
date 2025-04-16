import json

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from ..models.database import Keyword, Story
from ..models.story import StoryRequest, StoryResponse


class StoryGenerator:
    """A class responsible for generating RPG one-shot stories using OpenAI's GPT models.

    This class handles the entire story generation process, including:
    - Generating story content using GPT models
    - Extracting keywords from generated stories
    - Saving stories and keywords to the database

    Attributes:
        llm (ChatOpenAI): The language model used for story generation
        parser (PydanticOutputParser): Parser for converting model output to StoryResponse objects
    """

    def __init__(self, openai_api_key: str) -> None:
        """Initialize the StoryGenerator with OpenAI API key.

        Args:
            openai_api_key (str): The OpenAI API key for authentication
        """
        self.llm = ChatOpenAI(
            model="gpt-4.1-nano",
            temperature=0.7,
            openai_api_key=openai_api_key,
        )
        self.parser: PydanticOutputParser[StoryResponse] = PydanticOutputParser(
            pydantic_object=StoryResponse
        )

    async def extract_keywords(self, story: StoryResponse) -> list[str]:
        """Extract relevant keywords from a generated story.

        Uses GPT to analyze the story content and extract important keywords for
        searching and categorization. Keywords focus on themes, locations, character
        types, and important items.

        Args:
            story (StoryResponse): The generated story to extract keywords from

        Returns:
            list[str]: A list of extracted keywords
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a keyword extractor for RPG stories. Extract the most important keywords that would be useful for searching and categorization.
            Focus on themes, locations, character types, and important items.
            Format your response as a valid JSON array of strings, and nothing else.""",
                ),
                (
                    "user",
                    f"""Extract keywords from this story:

            Title: {story.title}
            Summary: {story.summary}
            Plot Points: {", ".join(story.plot_points)}
            Characters: {", ".join(story.characters)}
            Locations: {", ".join(story.locations)}
            Items: {", ".join(story.items)}

            Return ONLY a JSON array of keywords.""",
                ),
            ]
        )

        response = await (prompt | self.llm).ainvoke({})
        try:
            # Try to parse the response as JSON
            content = response.content
            if isinstance(content, str):
                keywords = json.loads(content)
                if isinstance(keywords, list):
                    return [str(k) for k in keywords]
            return []
        except json.JSONDecodeError:
            # If parsing fails, try to extract array-like content
            if isinstance(content, str):
                content = content.strip()
                if content.startswith("[") and content.endswith("]"):
                    try:
                        keywords = json.loads(content)
                        if isinstance(keywords, list):
                            return [str(k) for k in keywords]
                    except json.JSONDecodeError:
                        pass
            return []

    async def save_to_database(
        self,
        story: StoryResponse,
        request: StoryRequest,
        keywords: list[str],
        db: Session,
    ) -> Story:
        """Save a generated story and its keywords to the database.

        Creates a new story record in the database and associates it with
        extracted keywords. If keywords don't exist, they are created.

        Args:
            story (StoryResponse): The generated story to save
            request (StoryRequest): The original story generation request
            keywords (list[str]): List of keywords extracted from the story
            db (Session): Database session

        Returns:
            Story: The saved story database record
        """
        # Create story record
        db_story = Story(
            title=story.title,
            summary=story.summary,
            plot_points=json.dumps(list(story.plot_points)),
            characters=json.dumps(list(story.characters)),
            locations=json.dumps(list(story.locations)),
            items=json.dumps(list(story.items)),
            estimated_duration=story.estimated_duration,
            rpg_system=request.rpg_system,
            theme=request.theme,
            player_count=request.player_count,
            complexity=request.complexity,
        )

        # Add story to session
        db.add(db_story)
        db.flush()  # Flush to get the story ID

        # Add keywords
        for keyword_text in keywords:
            # Get or create keyword
            keyword = db.query(Keyword).filter(Keyword.keyword == keyword_text).first()
            if not keyword:
                keyword = Keyword(keyword=keyword_text)
                db.add(keyword)
                db.flush()

            # Associate keyword with story
            db_story.keywords.append(keyword)

        db.commit()
        db.refresh(db_story)
        return db_story

    async def generate_story(self, request: StoryRequest, db: Session) -> Story:
        """Generate a complete RPG one-shot story based on the request parameters.

        This is the main method that orchestrates the story generation process:
        1. Generates the story content using GPT
        2. Extracts keywords from the generated story
        3. Saves the story and keywords to the database

        Args:
            request (StoryRequest): The story generation request containing parameters
            db (Session): Database session

        Returns:
            Story: The saved story database record

        Raises:
            ValueError: If the generated story content is invalid
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert RPG story generator. Create an engaging one-shot story
            based on the provided parameters. The story should be complete and ready to play.

            The output should be a JSON object with the following fields:
            - title: string
            - summary: string
            - plot_points: array of strings
            - characters: array of strings
            - locations: array of strings
            - items: array of strings
            - estimated_duration: string""",
                ),
                (
                    "user",
                    """Generate a {length} {rpg_system} one-shot story with the following parameters:
            - Theme: {theme}
            - Player Count: {player_count}
            - Complexity: {complexity}
            {custom_theme_text}

            Please provide a complete story with all required fields.""",
                ),
            ]
        )

        custom_theme_text = (
            f"- Custom Theme: {request.custom_theme}" if request.custom_theme else ""
        )

        chain = prompt | self.llm | self.parser
        story_response = await chain.ainvoke(
            {
                "length": request.length,
                "rpg_system": request.rpg_system,
                "theme": request.theme,
                "player_count": request.player_count,
                "complexity": request.complexity,
                "custom_theme_text": custom_theme_text,
            }
        )

        # Extract keywords
        keywords = await self.extract_keywords(story_response)

        # Save to database
        db_story = await self.save_to_database(story_response, request, keywords, db)

        return db_story

    def parse_story_parts(self, story_text: str) -> list[str]:
        """Parse a story text into individual plot points.

        Splits the story text into parts based on newlines and filters out
        empty lines to create a list of plot points.

        Args:
            story_text (str): The complete story text to parse

        Returns:
            list[str]: List of individual plot points
        """
        # Split the story into parts based on newlines and filter out empty lines
        story_parts = [part.strip() for part in story_text.split("\n") if part.strip()]
        return story_parts
