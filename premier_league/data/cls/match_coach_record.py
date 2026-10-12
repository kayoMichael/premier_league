from dataclasses import dataclass
from typing import Optional

@dataclass
class MatchCoachRecord:
    match_id: Optional[int] = None
    team_id: Optional[int] = None
    coach_id: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
