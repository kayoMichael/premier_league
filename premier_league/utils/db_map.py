TEAM_STAT_KEYS: dict[str, str] = {
    # Expected goals
    "expected_goals": "xg",
    "expected_goals_on_target": "xgot",
    "expected_goals_open_play": "xg_open_play",
    "expected_goals_set_play": "xg_set_play",
    "expected_goals_non_penalty": "xg_non_penalty",

    # Possession / attack
    "BallPossesion": "possession",
    "ball_possession": "possession",
    "total_shots": "total_shots",
    "ShotsOnTarget": "shots_on_target",
    "ShotsOffTarget": "shots_off_target",
    "blocked_shots": "blocked_shots",
    "shots_woodwork": "hit_woodwork",
    "shots_inside_box": "shots_inside_box",
    "shots_outside_box": "shots_outside_box",
    "big_chance": "big_chances",
    "big_chances": "big_chances",
    "big_chance_missed_title": "big_chances_missed",
    "touches_opp_box": "touches_in_opposition_box",
    "dribbles_succeeded": "successful_dribbles",
    "corners": "corners",
    "Offsides": "offsides",

    # Passing
    "accurate_passes": "accurate_passes",
    "passes": "total_passes",
    "long_balls_accurate": "accurate_long_balls",
    "accurate_crosses": "accurate_crosses",

    # Defending / goalkeeping
    "matchstats.headers.tackles": "tackles",
    "tackles": "tackles",
    "interceptions": "interceptions",
    "shot_blocks": "blocks",
    "clearances": "clearances",
    "keeper_saves": "keeper_saves",

    # Duels / discipline
    "duel_won": "duels_won",
    "ground_duels_won": "ground_duels_won",
    "aerials_won": "aerial_duels_won",
    "fouls": "fouls_committed",
    "yellow_cards": "yellow_cards",
    "red_cards": "red_cards",
}


PLAYER_STAT_KEYS: dict[str, str] = {
    # Core
    "rating_title": "rating",
    "minutes_played": "minutes",

    # Attacking
    "goals": "goals",
    "assists": "assists",
    "expected_goals": "xg",
    "expected_assists": "xa",
    "expected_goals_on_target_variant": "xgot",
    "expected_goals_non_penalty": "xg_non_penalty",
    "xg_and_xa": "xg_plus_xa",
    "total_shots": "total_shots",
    "ShotsOnTarget": "shots_on_target",
    "ShotsOffTarget": "shots_off_target",
    "blocked_shots": "blocked_shots",
    "shots_woodwork": "hit_woodwork",
    "shot_accuracy": "shot_accuracy_pct",
    "touches_opp_box": "touches_in_opposition_box",
    "dribbles_succeeded": "successful_dribbles",
    "big_chance_missed_title": "big_chances_missed",
    "big_chance_created_team_title": "big_chances_created",
    "chances_created": "chances_created",
    "Offsides": "offsides",
    "corners": "corners_taken",

    # Passing
    "accurate_passes": "accurate_passes",
    "passes_into_final_third": "passes_into_final_third",
    "accurate_crosses": "accurate_crosses",
    "long_balls_accurate": "accurate_long_balls",

    # Possession
    "touches": "touches",
    "dispossessed": "dispossessed",

    # Defending
    "defensive_actions": "defensive_actions",
    "matchstats.headers.tackles": "tackles",
    "tackles": "tackles",
    "interceptions": "interceptions",
    "shot_blocks": "blocks",
    "recoveries": "recoveries",
    "clearances": "clearances",
    "headed_clearance": "headed_clearances",
    "clearance_off_the_line": "clearances_off_the_line",
    "errors_led_to_goal": "errors_led_to_goal",
    "penalty_conceded": "penalties_conceded",
    "dribbled_past": "dribbled_past",

    # Duels / discipline
    "duel_won": "duels_won",
    "duel_lost": "duels_lost",
    "ground_duels_won": "ground_duels_won",
    "aerials_won": "aerial_duels_won",
    "fouls": "fouls_committed",
    "was_fouled": "was_fouled",

    # Goalkeeper
    "saves": "saves",
    "saves_inside_box": "saves_inside_box",
    "diving_saves": "diving_saves",
    "goals_conceded": "goals_conceded",
    "expected_goals_on_target_faced": "xgot_faced",
    "goals_prevented": "goals_prevented",
    "keeper_sweeper": "acted_as_sweeper",
    "keeper_high_claim": "high_claims",
    "punches": "punches",
    "throws": "throws",
}


FUN_FACT_KEYS: dict[str, str] = {
    "fun_fact_made_mistake_led_to_goal": "errors_led_to_goal",
    "fun_fact_made_mistake_led_to_goal_plurals": "errors_led_to_goal",
    "fun_fact_conceded_penalty": "penalties_conceded",
    "fun_fact_conceded_penalty_plurals": "penalties_conceded",
}


WEATHER_KEYS: dict[str, str] = {
    "temperature": "weather_temperature",
    "windSpeed": "weather_wind_speed",
    "windDirectionCardinal": "weather_wind_direction",
    "iconCode": "weather_icon_code",
    "relativeHumidity": "weather_humidity_pct",
    "precipitation": "weather_precipitation",
    "snow": "weather_snow",
    "cloudCover": "weather_cloud_cover_pct",
    "description": "weather_description",
    "apiUsed": "weather_api_used",
    "lastUpdated": "weather_last_updated",
    "localizedKey": "weather_localized_key",
    "defaultTitle": "weather_default_title",
}


POSITION_NAMES: dict[int, str] = {
    0: "Goalkeeper",
    1: "Defender",
    2: "Midfielder",
    3: "Attacker",
}