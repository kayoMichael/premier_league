from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Index
from sqlalchemy.orm import relationship
from premier_league.data.models.base import Base

class Game(Base):
    __tablename__ = 'game'
    id = Column(String, primary_key=True)
    home_team_id = Column(String, ForeignKey('team.id'))
    away_team_id = Column(String, ForeignKey('team.id'))
    league_id = Column(Integer, ForeignKey('league.id'))
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    home_team_points = Column(Integer)
    away_team_points = Column(Integer)
    date = Column(DateTime, index=True)
    match_week = Column(Integer, index=True)
    season = Column(String)

    home_team = relationship('Team', foreign_keys=[home_team_id], back_populates='home_games')
    away_team = relationship('Team', foreign_keys=[away_team_id], back_populates='away_games')
    league = relationship('League', back_populates='games')
    game_stats = relationship('GameStats', back_populates='game')

    __table_args__ = (
        Index('idx_game_season_week', 'season', 'match_week'),
        Index('idx_game_teams', 'home_team_id', 'away_team_id'),
    )