from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from premier_league.data.models.base import Base


class GameStats(Base):
    __tablename__ = "game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey("game.id"))
    team_id = Column(String, ForeignKey("team.id"))

    game = relationship("Game", uselist=False, back_populates="game_stats")
    team = relationship("Team", back_populates="game_stats")

    # Expected goals and assists
    xG = Column(Float)
    xA = Column(Float)
    xAG = Column(Float)

    # Shots
    shots_total_FW = Column(Integer)
    shots_total_MF = Column(Integer)
    shots_total_DF = Column(Integer)
    shots_on_target_FW = Column(Integer)
    shots_on_target_MF = Column(Integer)
    shots_on_target_DF = Column(Integer)

    # Chance creation
    shot_creating_chances_FW = Column(Integer)
    shot_creating_chances_MF = Column(Integer)
    shot_creating_chances_DF = Column(Integer)
    goal_creating_actions_FW = Column(Integer)
    goal_creating_actions_MF = Column(Integer)
    goal_creating_actions_DF = Column(Integer)

    # Passing Stats
    passes_completed_FW = Column(Integer)
    passes_completed_MF = Column(Integer)
    passes_completed_DF = Column(Integer)
    pass_completion_percentage_FW = Column(Float)
    pass_completion_percentage_MF = Column(Float)
    pass_completion_percentage_DF = Column(Float)
    key_passes = Column(Integer)
    passes_into_final_third = Column(Integer)
    passes_into_penalty_area = Column(Integer)
    crosses_into_penalty_area = Column(Integer)
    progressive_passes = Column(Integer)

    # Defensive Stats
    tackles_won_FW = Column(Integer)
    tackles_won_MF = Column(Integer)
    tackles_won_DF = Column(Integer)
    dribblers_challenged_won_FW = Column(Integer)
    dribblers_challenged_won_MF = Column(Integer)
    dribblers_challenged_won_DF = Column(Integer)
    blocks_FW = Column(Integer)
    blocks_MF = Column(Integer)
    blocks_DF = Column(Integer)
    interceptions_FW = Column(Integer)
    interceptions_MF = Column(Integer)
    interceptions_DF = Column(Integer)
    clearances_FW = Column(Integer)
    clearances_MF = Column(Integer)
    clearances_DF = Column(Integer)
    errors_leading_to_goal = Column(Integer)

    # Possession Stats
    possession_rate = Column(Integer)
    touches_FW = Column(Integer)
    touches_MF = Column(Integer)
    touches_DF = Column(Integer)
    touches_att_pen_area_FW = Column(Integer)
    touches_att_pen_area_MF = Column(Integer)
    touches_att_pen_area_DF = Column(Integer)
    take_ons_FW = Column(Integer)
    take_ons_MF = Column(Integer)
    take_ons_DF = Column(Integer)
    successful_take_ons_FW = Column(Integer)
    successful_take_ons_MF = Column(Integer)
    successful_take_ons_DF = Column(Integer)
    carries_FW = Column(Integer)
    carries_MF = Column(Integer)
    carries_DF = Column(Integer)
    carries_into_penalty_area = Column(Integer)
    total_carrying_distance_FW = Column(Integer)
    total_carrying_distance_MF = Column(Integer)
    total_carrying_distance_DF = Column(Integer)
    dispossessed_FW = Column(Integer)
    dispossessed_MF = Column(Integer)
    dispossessed_DF = Column(Integer)
    aerials_won_FW = Column(Integer)
    aerials_won_MF = Column(Integer)
    aerials_won_DF = Column(Integer)
    aerials_lost_FW = Column(Integer)
    aerials_lost_MF = Column(Integer)
    aerials_lost_DF = Column(Integer)
    miss_controlled_FW = Column(Integer)
    miss_controlled_MF = Column(Integer)
    miss_controlled_DF = Column(Integer)

    # Goalkeeping Stats
    save_percentage = Column(Float)
    saves = Column(Integer)
    PSxG = Column(Float)
    passes_completed_GK = Column(Integer)
    crosses_stopped = Column(Integer)
    passes_40_yard_completed_GK = Column(Integer)

    # Other Match Stats
    yellow_card = Column(Integer)
    red_card = Column(Integer)
    pens_won = Column(Integer)
    pens_conceded = Column(Integer)
    fouls_committed_FW = Column(Integer)
    fouls_committed_MF = Column(Integer)
    fouls_committed_DF = Column(Integer)
    fouls_drawn_FW = Column(Integer)
    fouls_drawn_MF = Column(Integer)
    fouls_drawn_DF = Column(Integer)
    offside_FW = Column(Integer)
    offside_MF = Column(Integer)
    offside_DF = Column(Integer)

    __table_args__ = (Index("idx_game_team_stats", "game_id", "team_id", unique=True),)

    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        return result
