from sqlalchemy import Column, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from premier_league.data.models.base import Base


class GameStats(Base):
    __tablename__ = "game_stats"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.id', unique=True), unique=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    team_ranking_score = Column(Integer)

    game = relationship('Game', uselist=False, back_populates='game_stats')
    team = relationship('Team', back_populates='game_stats')

    # Expected goals and assists
    npxG = Column(Float)
    xA = Column(Float)
    xAG = Column(Float)

    # Shots
    shots_total_FW = Column(Integer)
    shots_total_MF = Column(Integer)
    shots_total_DEF = Column(Integer)
    shots_on_target_FW = Column(Integer)
    shots_on_target_MF = Column(Integer)
    shots_on_target_DEF = Column(Integer)

    # Chance creation
    shot_creating_chances_FW = Column(Integer)
    shot_creating_chances_MF = Column(Integer)
    shot_creating_chances_DEF = Column(Integer)
    goal_creating_actions_FW = Column(Integer)
    goal_creating_actions_MF = Column(Integer)
    goal_creating_actions_DEF = Column(Integer)

    # Passing Stats
    passes_completed_FW = Column(Integer)
    passes_completed_MF = Column(Integer)
    passes_completed_DEF = Column(Integer)
    pass_completion_percentage_FW = Column(Float)
    pass_completion_percentage_MF = Column(Float)
    pass_completion_percentage_DEF = Column(Float)
    total_passes_completed_FW = Column(Integer)
    total_passes_completed_MF = Column(Integer)
    total_passes_completed_DEF = Column(Integer)
    key_passes = Column(Integer)
    passes_into_final_third = Column(Integer)
    passes_into_penalty_area = Column(Integer)
    crosses_into_penalty_area = Column(Integer)
    progressive_passes = Column(Integer)

    # Defensive Stats
    tackles_won_FW = Column(Integer)
    tackles_won_MF = Column(Integer)
    tackles_won_DEF = Column(Integer)
    dribblers_challenged_won_FW = Column(Integer)
    dribblers_challenged_won_MF = Column(Integer)
    dribblers_challenged_won_DEF = Column(Integer)
    blocks_FW = Column(Integer)
    blocks_MF = Column(Integer)
    blocks_DEF = Column(Integer)
    interceptions_FW = Column(Integer)
    interceptions_MF = Column(Integer)
    interceptions_DEF = Column(Integer)
    clearances_FW = Column(Integer)
    clearances_MF = Column(Integer)
    clearances_DEF = Column(Integer)
    errors_leading_to_goal = Column(Integer)

    # Possession Stats
    touches_FW = Column(Integer)
    touches_MF = Column(Integer)
    touches_DEF = Column(Integer)
    touches_att_pen_area_FW = Column(Integer)
    touches_att_pen_area_MF = Column(Integer)
    touches_att_pen_area_DEF = Column(Integer)
    take_ons_FW = Column(Integer)
    take_ons_MF = Column(Integer)
    take_ons_DEF = Column(Integer)
    successful_take_ons_FW = Column(Integer)
    successful_take_ons_MF = Column(Integer)
    successful_take_ons_DEF = Column(Integer)
    carries_FW = Column(Integer)
    carries_MF = Column(Integer)
    carries_DEF = Column(Integer)
    total_carrying_distance_FW = Column(Integer)
    total_carrying_distance_MF = Column(Integer)
    total_carrying_distance_DEF = Column(Integer)
    dispossessed_FW = Column(Integer)
    dispossessed_MF = Column(Integer)
    dispossessed_DEF = Column(Integer)
    progressive_passes_FW = Column(Integer)
    progressive_passes_MF = Column(Integer)
    progressive_passes_DEF = Column(Integer)
    aeriels_won_FW = Column(Integer)
    aeriels_won_MF = Column(Integer)
    aeriels_won_DEF = Column(Integer)
    aeriels_lost_FW = Column(Integer)
    aeriels_lost_MF = Column(Integer)
    aeriels_lost_DEF = Column(Integer)

    # Goalkeeping Stats
    save_percentage = Column(Float)
    saves = Column(Integer)
    psxG = Column(Float)
    pass_completion_rate_GK = Column(Integer)
    passes_attempted_GK = Column(Integer)
    crosses_stopped = Column(Integer)
    crosses_stopped_rate = Column(Float)
    average_length_of_goal_kick = Column(Float)
    defensive_actions_outside_box = Column(Integer)

    # Other Match Stats
    penalty_kicks_made = Column(Integer)
    yellow_card = Column(Integer)
    red_card = Column(Integer)
    fouls = Column(Integer)
    fouls_drawn = Column(Integer)
    corners = Column(Integer)
    crosses = Column(Integer)
    long_balls = Column(Integer)

    __table_args__ = (
        Index('idx_game_team_stats', 'game_id', 'team_id', unique=True),
    )
