from sqlalchemy import Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from premier_league.data.models.base import Base


class Team(Base):
    __tablename__ = "team"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    league_id = Column(Integer, ForeignKey("league.id"), nullable=False)
    home_games = relationship(
        "Game", foreign_keys="Game.home_team_id", back_populates="home_team"
    )
    away_games = relationship(
        "Game", foreign_keys="Game.away_team_id", back_populates="away_team"
    )
    game_stats = relationship("GameStats")
    league = relationship("League", back_populates="teams")

    __table_args__ = (Index("idx_team_name_league", "name", "league_id", unique=True),)
