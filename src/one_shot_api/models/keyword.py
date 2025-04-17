from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from one_shot_api.models.database import Base

# Association table for story-keyword relationship
story_keyword = Table(
    "story_keyword",
    Base.metadata,
    Column("story_id", Integer, ForeignKey("stories.id")),
    Column("keyword_id", Integer, ForeignKey("keywords.id")),
)


class Keyword(Base):
    """Model for storing keywords associated with stories."""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True, nullable=False)

    # Relationship with stories
    stories = relationship("Story", secondary=story_keyword, back_populates="keywords")
