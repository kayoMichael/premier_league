from dataclasses import dataclass
from typing import Optional

@dataclass
class ShotRecord:
    match_id: Optional[int] = None
    fotmob_shot_id: Optional[int] = None
    team_id: Optional[int] = None
    player_id: Optional[int] = None
    keeper_id: Optional[int] = None
    minute: Optional[int] = None
    added_time: Optional[int] = None
    period: Optional[str] = None
    event_type_raw: Optional[str] = None
    outcome: Optional[str] = None            # Goal | Saved | Blocked | Miss | Post
    shot_type: Optional[str] = None
    body_part: Optional[str] = None          # Head | Left foot | Right foot | Other
    situation: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    blocked_x: Optional[float] = None
    blocked_y: Optional[float] = None
    goal_crossed_y: Optional[float] = None
    goal_crossed_z: Optional[float] = None
    on_goal_x: Optional[float] = None
    on_goal_y: Optional[float] = None
    on_goal_zoom_ratio: Optional[float] = None
    xg: Optional[float] = None
    xgot: Optional[float] = None
    is_goal: Optional[bool] = None
    is_own_goal: Optional[bool] = None
    is_big_chance: Optional[bool] = None
    is_blocked: Optional[bool] = None
    is_saved: Optional[bool] = None
    is_on_target: Optional[bool] = None
    is_from_penalty: Optional[bool] = None
    is_header: Optional[bool] = None
    is_from_inside_box: Optional[bool] = None
    is_saved_off_line: Optional[bool] = None