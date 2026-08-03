from dataclasses import dataclass
from typing import Optional

@dataclass
class TeamStatsRecord:
    match_id: Optional[int] = None
    team_id: Optional[int] = None
    period: str = "All"          # 'All' | 'FirstHalf' | 'SecondHalf' | extra-time keys
    is_home: Optional[bool] = None
    formation: Optional[str] = None
    xg: Optional[float] = None
    xgot: Optional[float] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    blocked_shots: Optional[int] = None
    big_chances: Optional[int] = None
    big_chances_missed: Optional[int] = None
    possession_pct: Optional[float] = None
    total_passes: Optional[int] = None
    accurate_passes: Optional[int] = None
    pass_accuracy_pct: Optional[float] = None
    fouls: Optional[int] = None
    offsides: Optional[int] = None
    corners: Optional[int] = None
    tackles: Optional[int] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    blocks: Optional[int] = None
    duels_won: Optional[int] = None
    aerial_duels_won: Optional[int] = None
    saves: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None