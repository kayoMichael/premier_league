TEAM_STAT_MAP = {
    "BallPossesion": "possession_pct",  # sic — FotMob's typo
    "expected_goals": "xg",
    "expected_goals_on_target": "xgot",
    "total_shots": "shots",
    "ShotsOnTarget": "shots_on_target",
    "blocked_shots": "blocked_shots",
    "big_chance": "big_chances",
    "big_chance_missed_title": "big_chances_missed",
    "passes": "total_passes",
    "fouls": "fouls",
    "Offsides": "offsides",
    "corners": "corners",
    "matchstats.headers.tackles": "tackles",
    "interceptions": "interceptions",
    "clearances": "clearances",
    "shot_blocks": "blocks",
    "duel_won": "duels_won",
    "keeper_saves": "saves",
    "yellow_cards": "yellow_cards",
    "red_cards": "red_cards",
}
# team keys that arrive as "485 (87%)" -> (count_column, pct_column)
TEAM_FRACTION_MAP = {
    "accurate_passes": ("accurate_passes", "pass_accuracy_pct"),
    "aerials_won": ("aerial_duels_won", None),
}
# team keys we see but deliberately don't store (don't warn about these)
TEAM_IGNORED = {
    "shots", "expected_goals_open_play", "expected_goals_set_play",
    "expected_goals_non_penalty", "ShotsOffTarget", "shots_woodwork",
    "shots_inside_box", "shots_outside_box", "own_half_passes",
    "opposition_half_passes", "long_balls_accurate", "accurate_crosses",
    "player_throws", "touches_opp_box", "ground_duels_won",
    "dribbles_succeeded", "discipline", "duels", "defense", "passes",
}

PLAYER_STAT_MAP = {
    "rating_title": ("rating", float),
    "minutes_played": ("minutes_played", int),
    "goals": ("goals", int),
    "assists": ("assists", int),
    "expected_goals": ("xg", float),
    "expected_assists": ("xa", float),
    "xg_and_xa": ("xg_plus_xa", float),
    "expected_goals_on_target_variant": ("xgot", float),
    "total_shots": ("shots", int),
    "ShotsOnTarget": ("shots_on_target", int),
    "blocked_shots": ("blocked_shots", int),
    "big_chance_missed_title": ("big_chances_missed", int),
    "big_chance_created_team_title": ("big_chances_created", int),
    "touches": ("touches", int),
    "touches_opp_box": ("touches_in_opposition_box", int),
    "chances_created": ("chances_created", int),
    "passes_into_final_third": ("passes_into_final_third", int),
    "matchstats.headers.tackles": ("tackles_won", int),
    "interceptions": ("interceptions", int),
    "recoveries": ("recoveries", int),
    "clearances": ("clearances", int),
    "headed_clearance": ("headed_clearances", int),
    "shot_blocks": ("blocks", int),
    "duel_won": ("duels_won", int),
    "was_fouled": ("fouls_won", int),
    "fouls": ("fouls_committed", int),
    "Offsides": ("offsides", int),
    "conceded_penalties": ("penalties_conceded", int),
    "dispossessed": ("dispossessed", int),
    "dribbled_past": ("dribbled_past", int),
    # keeper
    "saves": ("saves", int),
    "goals_conceded": ("goals_conceded", int),
    "goals_prevented": ("goals_prevented", float),
    "punches": ("punches", int),
    "keeper_high_claim": ("high_claims", int),
    "keeper_sweeper": ("sweeper_actions", int),
}
# fractionWithPercentage keys -> (value_col, total_col, pct_col_or_None)
PLAYER_FRACTION_MAP = {
    "accurate_passes": ("accurate_passes", "total_passes", "pass_accuracy_pct"),
    "long_balls_accurate": ("accurate_long_balls", "attempted_long_balls", None),
    "accurate_crosses": ("accurate_crosses", "attempted_crosses", None),
    "dribbles_succeeded": ("successful_dribbles", "attempted_dribbles", "dribble_success_pct"),
    "ground_duels_won": ("ground_duels_won", "ground_duels_attempted", None),
    "aerials_won": ("aerial_duels_won", "aerial_duels_attempted", None),
}
PLAYER_IGNORED = {
    "Shotmap", "defensive_actions", "shot_accuracy", "ShotsOffTarget",
    "expected_goals_non_penalty",
    "duel_lost", "keeper_diving_save", "saves_inside_box", "player_throws",
    "expected_goals_on_target_faced", "corners",
}

SHOT_OUTCOME = {  # eventType (+isBlocked) -> outcome label
    "Goal": "Goal", "Miss": "Miss", "Post": "Post",
}
BODY_PART = {"Header": "Head", "LeftFoot": "Left foot", "RightFoot": "Right foot"}