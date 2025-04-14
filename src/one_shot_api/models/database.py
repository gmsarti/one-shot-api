from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from ..utils.database import Base

# Association table for story-keyword relationship
story_keyword = Table(
    "story_keyword",
    Base.metadata,
    Column("story_id", Integer, ForeignKey("stories.id")),
    Column("keyword_id", Integer, ForeignKey("keywords.id")),
)


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(String)
    plot_points = Column(String)  # Stored as JSON string
    characters = Column(String)  # Stored as JSON string
    locations = Column(String)  # Stored as JSON string
    items = Column(String)  # Stored as JSON string
    estimated_duration = Column(String)
    rpg_system = Column(String)
    theme = Column(String)
    player_count = Column(Integer)
    complexity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with keywords
    keywords = relationship(
        "Keyword", secondary=story_keyword, back_populates="stories"
    )


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, unique=True, index=True)

    # Relationship with stories
    stories = relationship("Story", secondary=story_keyword, back_populates="keywords")
