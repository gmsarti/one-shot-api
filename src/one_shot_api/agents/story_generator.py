import json

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from ..models.database import Keyword, Story
from ..models.story import StoryRequest, StoryResponse


class StoryGenerator:
    def __init__(self, openai_api_key: str) -> None:
        self.llm = ChatOpenAI(
            model="gpt-4-mini",
            temperature=0.7,
            openai_api_key=openai_api_key,
        )
        self.parser = PydanticOutputParser(pydantic_object=StoryResponse)

    async def extract_keywords(self, story: StoryResponse) -> list[str]:
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
            keywords = json.loads(response.content)
            if isinstance(keywords, list):
                return keywords
            return []
        except json.JSONDecodeError:
            # If parsing fails, try to extract array-like content
            content = response.content.strip()
            if content.startswith("[") and content.endswith("]"):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return []
            return []

    async def save_to_database(
        self,
        story: StoryResponse,
        request: StoryRequest,
        keywords: list[str],
        db: Session,
    ) -> Story:
        # Create story record
        db_story = Story(
            title=story.title,
            summary=story.summary,
            plot_points=json.dumps(story.plot_points),
            characters=json.dumps(story.characters),
            locations=json.dumps(story.locations),
            items=json.dumps(story.items),
            estimated_duration=story.estimated_duration,
            rpg_system=request.rpg_system,
            theme=request.theme,
            player_count=request.player_count,
            complexity=request.complexity,
        )

        # Add keywords
        for keyword_text in keywords:
            # Get or create keyword
            keyword = db.query(Keyword).filter(Keyword.keyword == keyword_text).first()
            if not keyword:
                keyword = Keyword(keyword=keyword_text)
                db.add(keyword)
                db.flush()

            db_story.keywords.append(keyword)

        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        return db_story

    async def generate_story(self, request: StoryRequest, db: Session) -> Story:
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

    def _parse_story_parts(self, story_text: str) -> list[str]:
        # Split the story into parts based on newlines and filter out empty lines
        story_parts = [part.strip() for part in story_text.split("\n") if part.strip()]
        return story_parts
