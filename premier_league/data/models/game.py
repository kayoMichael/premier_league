from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from premier_league.data.models.base import Base


class Game(Base):
    __tablename__ = "game"
    id = Column(String, primary_key=True)
    home_team_id = Column(String, ForeignKey("team.id"))
    away_team_id = Column(String, ForeignKey("team.id"))
    league_id = Column(Integer, ForeignKey("league.id"))
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    home_team_points = Column(Integer)
    away_team_points = Column(Integer)
    date = Column(DateTime, index=True)
    match_week = Column(Integer, index=True)
    season = Column(String)

    home_team = relationship(
        "Team", foreign_keys=[home_team_id], back_populates="home_games"
    )
    away_team = relationship(
        "Team", foreign_keys=[away_team_id], back_populates="away_games"
    )
    league = relationship("League", back_populates="games")
    game_stats = relationship("GameStats", back_populates="game")

    __table_args__ = (
        Index("idx_game_season_week", "season", "match_week"),
        Index("idx_game_teams", "home_team_id", "away_team_id"),
    )

    def to_dict(self, include_relationships=False):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if result["date"]:
            result["date"] = result["date"].isoformat()

        if include_relationships:
            if self.home_team:
                result["home_team"] = {
                    "id": self.home_team.id,
                    "name": self.home_team.name,
                }

            if self.away_team:
                result["away_team"] = {
                    "id": self.away_team.id,
                    "name": self.away_team.name,
                }

            if self.game_stats:
                result["game_stats"] = [stat.to_dict() for stat in self.game_stats]

            if self.league:
                result["league"] = {"id": self.league.id, "name": self.league.name}

        return result
