from dataclasses import dataclass
from typing import Optional

@dataclass
class EventRecord:
    match_id: Optional[int] = None
    fotmob_event_id: Optional[int] = None
    team_id: Optional[int] = None
    player_id: Optional[int] = None
    related_player_id: Optional[int] = None
    minute: Optional[int] = None
    added_time: Optional[int] = None
    event_type: Optional[str] = None
    event_type_raw: Optional[str] = None
    event_description: Optional[str] = None
    is_home: Optional[bool] = None
    is_goal: Optional[bool] = None
    is_own_goal: Optional[bool] = None
    is_penalty: Optional[bool] = None
    is_penalty_shootout: Optional[bool] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    card_type: Optional[str] = None
    sort_order: Optional[int] = None
