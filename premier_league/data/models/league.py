from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..models.base import Base


class League(Base):
    __tablename__ = "league"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    games = relationship("Game", back_populates="league")
    teams = relationship("Team", back_populates="league")
    up_to_date_season = Column(String)
    up_to_date_match_week = Column(Integer)
