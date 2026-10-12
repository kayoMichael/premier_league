from dataclasses import dataclass
from typing import Optional

@dataclass
class AppearanceRecord:
    match_id: Optional[int] = None
    player_id: Optional[int] = None
    player_name: Optional[str] = None       # observability only; not a DB column
    team_id: Optional[int] = None
    is_starter: Optional[bool] = None
    is_substitute: Optional[bool] = None
    shirt_number: Optional[int] = None
    minute_entered: Optional[int] = None
    minute_left: Optional[int] = None
    minutes_played: Optional[int] = None
    rating: Optional[float] = None
    player_of_match: Optional[bool] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    xg: Optional[float] = None
    xa: Optional[float] = None
    xg_plus_xa: Optional[float] = None
    xgot: Optional[float] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    blocked_shots: Optional[int] = None
    big_chances_missed: Optional[int] = None
    big_chances_created: Optional[int] = None
    touches: Optional[int] = None
    touches_in_opposition_box: Optional[int] = None
    successful_dribbles: Optional[int] = None
    attempted_dribbles: Optional[int] = None
    dribble_success_pct: Optional[float] = None
    accurate_passes: Optional[int] = None
    total_passes: Optional[int] = None
    pass_accuracy_pct: Optional[float] = None
    chances_created: Optional[int] = None
    accurate_crosses: Optional[int] = None
    attempted_crosses: Optional[int] = None
    accurate_long_balls: Optional[int] = None
    attempted_long_balls: Optional[int] = None
    passes_into_final_third: Optional[int] = None
    tackles_won: Optional[int] = None
    interceptions: Optional[int] = None
    recoveries: Optional[int] = None
    clearances: Optional[int] = None
    headed_clearances: Optional[int] = None
    blocks: Optional[int] = None
    duels_won: Optional[int] = None
    duels_attempted: Optional[int] = None
    ground_duels_won: Optional[int] = None
    ground_duels_attempted: Optional[int] = None
    aerial_duels_won: Optional[int] = None
    aerial_duels_attempted: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_won: Optional[int] = None
    offsides: Optional[int] = None
    penalties_conceded: Optional[int] = None
    # keeper
    saves: Optional[int] = None
    goals_conceded: Optional[int] = None
    goals_prevented: Optional[float] = None
    clean_sheet: Optional[bool] = None
    punches: Optional[int] = None
    high_claims: Optional[int] = None
    sweeper_actions: Optional[int] = None
    dispossessed: Optional[int] = None
    dribbled_past: Optional[int] = None
    market_value: Optional[int] = None       # valuation snapshot at match time
    age_at_match: Optional[int] = None


    
