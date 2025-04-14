from enum import Enum

from pydantic import BaseModel, Field


class RPGSystem(str, Enum):
    DND_5E = "D&D 5e"
    PATHFINDER = "Pathfinder"
    CALL_OF_CTHULHU = "Call of Cthulhu"
    CUSTOM = "Custom"


class StoryLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class StoryTheme(str, Enum):
    FANTASY = "fantasy"
    HORROR = "horror"
    SCI_FI = "sci-fi"
    MYSTERY = "mystery"
    CUSTOM = "custom"


class StoryRequest(BaseModel):
    rpg_system: RPGSystem = Field(
        default=RPGSystem.DND_5E, description="The RPG system to generate the story for"
    )
    length: StoryLength = Field(
        default=StoryLength.MEDIUM, description="The length of the story"
    )
    theme: StoryTheme = Field(
        default=StoryTheme.FANTASY, description="The theme of the story"
    )
    custom_theme: str | None = Field(
        default=None, description="Custom theme description if theme is set to CUSTOM"
    )
    player_count: int = Field(default=4, ge=1, le=6, description="Number of players")
    complexity: int = Field(
        default=3, ge=1, le=5, description="Story complexity level (1-5)"
    )


class StoryResponse(BaseModel):
    title: str
    summary: str
    plot_points: list[str]
    characters: list[str]
    locations: list[str]
    items: list[str]
    estimated_duration: str
