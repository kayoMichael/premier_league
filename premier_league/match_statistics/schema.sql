-- =============================================================================
-- Premier League Library — SQLite schema
-- FotMob-sourced football database.
--
-- Initialize once:   sqlite3 pl.db < schema.sql
-- or in Python:      conn.executescript(open("schema.sql").read())
--
-- Design notes:
--   * Natural FotMob IDs are the PKs for leagues, teams, players, matches
--     (idempotent upserts). Seasons/events/shots/awards/squads use surrogate ids.
--   * appearances + match_team_stats are the source of truth.
--     player_seasons + team_seasons are recomputed aggregate CACHES — do not
--     mix the two grains in one query or you double-count.
--   * average_rating and any *_pct column CANNOT be summed.
--   * Query the views (bottom) for team/player/match analytics, not the base
--     tables — they avoid hand-written home/away CASE logic.
-- =============================================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- LEAGUES
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leagues (
    id                INTEGER PRIMARY KEY,          -- FotMob league ID
    name              TEXT NOT NULL,
    country_code      TEXT,
    parent_league_id  INTEGER,
    logo_url          TEXT,
    page_url          TEXT,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_league_id) REFERENCES leagues(id)
);

-- -----------------------------------------------------------------------------
-- SEASONS  (surrogate PK; a season is not a single FotMob entity)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS seasons (
    id                INTEGER PRIMARY KEY,
    league_id         INTEGER NOT NULL,
    fotmob_season_id  INTEGER,
    name              TEXT NOT NULL,               -- e.g. "2024-2025"
    start_date        DATE,
    end_date          DATE,
    is_current        INTEGER DEFAULT 0,           -- boolean 0/1
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    UNIQUE (league_id, fotmob_season_id)
);

-- -----------------------------------------------------------------------------
-- TEAMS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS teams (
    id            INTEGER PRIMARY KEY,             -- FotMob team ID
    name          TEXT NOT NULL,
    short_name    TEXT,
    country_code  TEXT,
    logo_url      TEXT,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TEAM_SEASONS  (standings — CACHE, aggregated from match_team_stats)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS team_seasons (
    season_id             INTEGER NOT NULL,
    team_id               INTEGER NOT NULL,
    position              INTEGER,
    played                INTEGER,
    wins                  INTEGER,
    draws                 INTEGER,
    losses                INTEGER,
    goals_for             INTEGER,
    goals_against         INTEGER,
    goal_difference       INTEGER,
    points                INTEGER,
    home_played           INTEGER,
    home_wins             INTEGER,
    home_draws            INTEGER,
    home_losses           INTEGER,
    home_goals_for        INTEGER,
    home_goals_against    INTEGER,
    home_goal_difference  INTEGER,
    home_points           INTEGER,
    away_played           INTEGER,
    away_wins             INTEGER,
    away_draws            INTEGER,
    away_losses           INTEGER,
    away_goals_for        INTEGER,
    away_goals_against    INTEGER,
    away_goal_difference  INTEGER,
    away_points           INTEGER,
    form                  TEXT,
    qualification         TEXT,
    points_deduction      INTEGER,
    deduction_reason      TEXT,
    average_rating        REAL,
    expected_points       REAL,
    expected_position     REAL,
    standings_updated_at  DATETIME,
    created_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (season_id, team_id),
    FOREIGN KEY (season_id) REFERENCES seasons(id),
    FOREIGN KEY (team_id)   REFERENCES teams(id)
);

-- -----------------------------------------------------------------------------
-- PLAYERS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS players (
    id                INTEGER PRIMARY KEY,         -- FotMob player ID
    name              TEXT NOT NULL,
    first_name        TEXT,
    last_name         TEXT,
    common_name       TEXT,
    nationality       TEXT,
    country_code      TEXT,
    birth_date        DATE,
    height_cm         INTEGER,
    preferred_foot    TEXT,
    primary_position  TEXT,
    photo_url         TEXT,
    opta_id           TEXT,                        -- cross-reference to Opta datasets
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- PLAYER_SEASONS  (season totals — CACHE, aggregated from appearances)
-- One row per player per team per season (handles mid-season transfers).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS player_seasons (
    season_id                  INTEGER NOT NULL,
    player_id                  INTEGER NOT NULL,
    team_id                    INTEGER NOT NULL,
    appearances                INTEGER,
    starts                     INTEGER,
    substitute_appearances     INTEGER,
    minutes_played             INTEGER,
    goals                      INTEGER,
    assists                    INTEGER,
    goal_contributions         INTEGER,
    penalties_scored           INTEGER,
    penalties_missed           INTEGER,
    own_goals                  INTEGER,
    xg                         REAL,
    xa                         REAL,
    xg_plus_xa                 REAL,
    xg_on_target               REAL,
    shots                      INTEGER,
    shots_on_target            INTEGER,
    blocked_shots              INTEGER,
    big_chances                INTEGER,
    big_chances_missed         INTEGER,
    touches                    INTEGER,
    touches_in_opposition_box  INTEGER,
    successful_dribbles        INTEGER,
    attempted_dribbles         INTEGER,
    dribble_success_pct        REAL,
    accurate_passes            INTEGER,
    total_passes               INTEGER,
    pass_accuracy_pct          REAL,
    chances_created            INTEGER,
    big_chances_created        INTEGER,
    accurate_crosses           INTEGER,
    attempted_crosses          INTEGER,
    accurate_long_balls        INTEGER,
    attempted_long_balls       INTEGER,
    passes_into_final_third    INTEGER,
    tackles_won                INTEGER,
    tackles_attempted          INTEGER,
    interceptions              INTEGER,
    recoveries                 INTEGER,
    clearances                 INTEGER,
    headed_clearances          INTEGER,
    clearances_off_the_line    INTEGER,
    blocks                     INTEGER,
    duels_won                  INTEGER,
    duels_attempted            INTEGER,
    ground_duels_won           INTEGER,
    ground_duels_attempted     INTEGER,
    aerial_duels_won           INTEGER,
    aerial_duels_attempted     INTEGER,
    fouls_committed            INTEGER,
    fouls_won                  INTEGER,
    yellow_cards               INTEGER,
    second_yellow_cards        INTEGER,
    red_cards                  INTEGER,
    errors_led_to_shot         INTEGER,
    errors_led_to_goal         INTEGER,
    penalties_won              INTEGER,
    penalties_conceded         INTEGER,
    saves                      INTEGER,
    goals_conceded             INTEGER,
    goals_prevented            REAL,
    clean_sheets               INTEGER,
    punches                    INTEGER,
    high_claims                INTEGER,
    recoveries_as_keeper       INTEGER,
    sweeper_actions            INTEGER,
    accurate_keeper_passes     INTEGER,
    attempted_keeper_passes    INTEGER,
    keeper_pass_accuracy_pct   REAL,
    average_rating             REAL,
    player_of_match_awards     INTEGER,
    created_at                 DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at                 DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (season_id, player_id, team_id),
    FOREIGN KEY (season_id) REFERENCES seasons(id),
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (team_id)   REFERENCES teams(id)
);

-- -----------------------------------------------------------------------------
-- MATCHES  (match-level facts only; team stats -> match_team_stats)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS matches (
    id                       INTEGER PRIMARY KEY,  -- FotMob match ID
    season_id                INTEGER NOT NULL,
    home_team_id             INTEGER NOT NULL,
    away_team_id             INTEGER NOT NULL,
    page_url                 TEXT,
    kickoff_time_utc         DATETIME,
    status                   TEXT,
    round                    TEXT,
    round_name               TEXT,
    stage                    TEXT,
    match_name               TEXT,
    home_score               INTEGER,
    away_score               INTEGER,
    home_halftime_score      INTEGER,
    away_halftime_score      INTEGER,
    home_extra_time_score    INTEGER,
    away_extra_time_score    INTEGER,
    home_penalty_score       INTEGER,
    away_penalty_score       INTEGER,
    winner_team_id           INTEGER,              -- NULL for a draw
    result_string            TEXT,
    referee_name             TEXT,
    attendance               INTEGER,
    stadium_name             TEXT,
    stadium_city             TEXT,
    stadium_country          TEXT,
    stadium_lat              REAL,
    stadium_long             REAL,
    stadium_capacity         INTEGER,
    stadium_surface          TEXT,                 -- e.g. 'artificial turf'
    highlights_url           TEXT,                 -- YouTube highlights link
    scraped_at               DATETIME,
    created_at               DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at               DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (season_id)      REFERENCES seasons(id),
    FOREIGN KEY (home_team_id)   REFERENCES teams(id),
    FOREIGN KEY (away_team_id)   REFERENCES teams(id),
    FOREIGN KEY (winner_team_id) REFERENCES teams(id)
);

-- -----------------------------------------------------------------------------
-- MATCH_TEAM_STATS  (one row per team per match PER PERIOD)
-- period: 'All' = full match, plus 'FirstHalf', 'SecondHalf', and extra-time
-- periods when present. 'All' is NOT the sum of a subset — ALWAYS filter on
-- period (the views default to 'All'); summing across periods double-counts.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS match_team_stats (
    match_id           INTEGER NOT NULL,
    team_id            INTEGER NOT NULL,
    period             TEXT NOT NULL DEFAULT 'All',
    is_home            INTEGER NOT NULL,           -- boolean 0/1
    formation          TEXT,                       -- populated on 'All' rows only
    xg                 REAL,
    xgot               REAL,
    shots              INTEGER,
    shots_on_target    INTEGER,
    blocked_shots      INTEGER,
    big_chances        INTEGER,
    big_chances_missed INTEGER,
    possession_pct     REAL,
    total_passes       INTEGER,
    accurate_passes    INTEGER,
    pass_accuracy_pct  REAL,
    fouls              INTEGER,
    offsides           INTEGER,
    corners            INTEGER,
    tackles            INTEGER,
    interceptions      INTEGER,
    clearances         INTEGER,
    blocks             INTEGER,
    duels_won          INTEGER,
    aerial_duels_won   INTEGER,
    saves              INTEGER,
    yellow_cards       INTEGER,
    red_cards          INTEGER,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (match_id, team_id, period),
    UNIQUE (match_id, is_home, period),            -- can't have two home rows per period
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (team_id)  REFERENCES teams(id)
);

-- -----------------------------------------------------------------------------
-- MATCH_WEATHER  (1:1 optional with matches; sourced from the match page)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS match_weather (
    match_id         INTEGER PRIMARY KEY,
    temperature      REAL,
    wind_speed       REAL,
    wind_direction   TEXT,
    icon_code        INTEGER,
    humidity_pct     REAL,
    precipitation    REAL,
    snow             REAL,
    cloud_cover_pct  REAL,
    description      TEXT,
    localized_key    TEXT,
    default_title    TEXT,
    last_updated     DATETIME,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- -----------------------------------------------------------------------------
-- APPEARANCES  (per-player per-match — SOURCE OF TRUTH for player stats)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS appearances (
    match_id                   INTEGER NOT NULL,
    player_id                  INTEGER NOT NULL,
    team_id                    INTEGER NOT NULL,
    is_starter                 INTEGER,            -- boolean 0/1
    is_substitute              INTEGER,
    entered_match              INTEGER,
    left_match                 INTEGER,
    position                   TEXT,
    lineup_position            TEXT,
    formation_slot             TEXT,
    shirt_number               INTEGER,
    minute_entered             INTEGER,
    minute_left                INTEGER,
    minutes_played             INTEGER,
    rating                     REAL,
    player_of_match            INTEGER,            -- boolean 0/1
    captain                    INTEGER,            -- boolean 0/1
    goals                      INTEGER,
    assists                    INTEGER,
    own_goals                  INTEGER,
    penalties_scored           INTEGER,
    penalties_missed           INTEGER,
    xg                         REAL,
    xa                         REAL,
    xg_plus_xa                 REAL,
    xgot                       REAL,
    shots                      INTEGER,
    shots_on_target            INTEGER,
    blocked_shots              INTEGER,
    big_chances                INTEGER,
    big_chances_missed         INTEGER,
    touches                    INTEGER,
    touches_in_opposition_box  INTEGER,
    successful_dribbles        INTEGER,
    attempted_dribbles         INTEGER,
    dribble_success_pct        REAL,
    accurate_passes            INTEGER,
    total_passes               INTEGER,
    pass_accuracy_pct          REAL,
    chances_created            INTEGER,
    big_chances_created        INTEGER,
    accurate_crosses           INTEGER,
    attempted_crosses          INTEGER,
    accurate_long_balls        INTEGER,
    attempted_long_balls       INTEGER,
    passes_into_final_third    INTEGER,
    tackles_won                INTEGER,
    tackles_attempted          INTEGER,
    interceptions              INTEGER,
    recoveries                 INTEGER,
    clearances                 INTEGER,
    headed_clearances          INTEGER,
    clearances_off_the_line    INTEGER,
    blocks                     INTEGER,
    duels_won                  INTEGER,
    duels_attempted            INTEGER,
    ground_duels_won           INTEGER,
    ground_duels_attempted     INTEGER,
    aerial_duels_won           INTEGER,
    aerial_duels_attempted     INTEGER,
    fouls_committed            INTEGER,
    fouls_won                  INTEGER,
    offsides                   INTEGER,
    yellow_cards               INTEGER,
    second_yellow_cards        INTEGER,
    red_cards                  INTEGER,
    errors_led_to_shot         INTEGER,
    errors_led_to_goal         INTEGER,
    penalties_won              INTEGER,
    penalties_conceded         INTEGER,
    saves                      INTEGER,
    goals_conceded             INTEGER,
    goals_prevented            REAL,
    clean_sheet                INTEGER,            -- boolean 0/1
    punches                    INTEGER,
    high_claims                INTEGER,
    keeper_recoveries          INTEGER,
    sweeper_actions            INTEGER,
    accurate_keeper_passes     INTEGER,
    attempted_keeper_passes    INTEGER,
    keeper_pass_accuracy_pct   REAL,
    dispossessed               INTEGER,
    dribbled_past              INTEGER,
    market_value               INTEGER,            -- valuation snapshot at match time
    age_at_match               INTEGER,
    created_at                 DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at                 DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id)  REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (team_id)   REFERENCES teams(id)
);

-- -----------------------------------------------------------------------------
-- MATCH_EVENTS  (goals, cards, subs, VAR — the match timeline)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS match_events (
    id                   INTEGER PRIMARY KEY,
    match_id             INTEGER NOT NULL,
    fotmob_event_id      INTEGER,
    team_id              INTEGER,
    player_id            INTEGER,
    related_player_id    INTEGER,
    minute               INTEGER,
    added_time           INTEGER,
    period               TEXT,
    event_type           TEXT,
    event_type_raw       TEXT,
    event_description    TEXT,
    is_home              INTEGER,                  -- boolean 0/1
    is_goal              INTEGER,
    is_own_goal          INTEGER,
    is_penalty           INTEGER,
    is_penalty_shootout  INTEGER,
    is_var               INTEGER,
    is_cancelled         INTEGER,
    home_score           INTEGER,                  -- running score after event
    away_score           INTEGER,
    card_type            TEXT,
    var_decision         TEXT,
    sort_order           INTEGER,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id)          REFERENCES matches(id),
    FOREIGN KEY (team_id)           REFERENCES teams(id),
    FOREIGN KEY (player_id)         REFERENCES players(id),
    FOREIGN KEY (related_player_id) REFERENCES players(id)
);

-- -----------------------------------------------------------------------------
-- SHOTS  (shot map — one row per shot)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shots (
    id                   INTEGER PRIMARY KEY,
    fotmob_shot_id       INTEGER,
    match_id             INTEGER NOT NULL,
    match_event_id       INTEGER,
    team_id              INTEGER,
    player_id            INTEGER,
    keeper_id            INTEGER,
    minute               INTEGER,
    added_time           INTEGER,
    period               TEXT,
    outcome              TEXT,
    event_type_raw       TEXT,
    shot_type            TEXT,
    situation            TEXT,
    body_part            TEXT,
    x                    REAL,
    y                    REAL,
    blocked_x            REAL,
    blocked_y            REAL,
    goal_crossed_y       REAL,
    goal_crossed_z       REAL,
    on_goal_x            REAL,
    on_goal_y            REAL,
    on_goal_zoom_ratio   REAL,
    xg                   REAL,
    xgot                 REAL,
    is_goal              INTEGER,                  -- boolean 0/1
    is_own_goal          INTEGER,
    is_big_chance        INTEGER,
    is_blocked           INTEGER,
    is_saved             INTEGER,
    is_on_target         INTEGER,
    is_from_penalty      INTEGER,
    is_first_time        INTEGER,
    is_header            INTEGER,
    is_from_inside_box   INTEGER,
    is_saved_off_line    INTEGER,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id)       REFERENCES matches(id),
    FOREIGN KEY (match_event_id) REFERENCES match_events(id),
    FOREIGN KEY (team_id)        REFERENCES teams(id),
    FOREIGN KEY (player_id)      REFERENCES players(id),
    FOREIGN KEY (keeper_id)      REFERENCES players(id)
);

-- -----------------------------------------------------------------------------
-- SEASON_AWARDS  (Golden Boot, POTM, team-of-week ranks, etc.)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS season_awards (
    id           INTEGER PRIMARY KEY,
    season_id    INTEGER NOT NULL,
    player_id    INTEGER,
    team_id      INTEGER,
    award_type   TEXT,
    award_name   TEXT,
    rank         INTEGER,
    value        REAL,
    value_text   TEXT,
    source       TEXT,
    source_url   TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (season_id) REFERENCES seasons(id),
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (team_id)   REFERENCES teams(id)
);

-- -----------------------------------------------------------------------------
-- SEASON_SQUADS  (published XIs: team of the season, etc.)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS season_squads (
    id           INTEGER PRIMARY KEY,
    season_id    INTEGER NOT NULL,
    squad_type   TEXT,
    squad_name   TEXT,
    formation    TEXT,
    source       TEXT,
    source_url   TEXT,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (season_id) REFERENCES seasons(id)
);

-- -----------------------------------------------------------------------------
-- SEASON_SQUAD_PLAYERS  (members of a published squad)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS season_squad_players (
    season_squad_id  INTEGER NOT NULL,
    player_id        INTEGER NOT NULL,
    team_id          INTEGER,
    position         TEXT,
    formation_slot   TEXT,
    selection_order  INTEGER,
    rank             INTEGER,
    rating           REAL,
    is_captain       INTEGER,                      -- boolean 0/1
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (season_squad_id, player_id),
    FOREIGN KEY (season_squad_id) REFERENCES season_squads(id),
    FOREIGN KEY (player_id)       REFERENCES players(id),
    FOREIGN KEY (team_id)         REFERENCES teams(id)
);

-- -----------------------------------------------------------------------------
-- COACHES  (managers; from lineup.<side>.coach)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coaches (
    id            INTEGER PRIMARY KEY,             -- FotMob coach ID
    name          TEXT NOT NULL,
    first_name    TEXT,
    last_name     TEXT,
    country_code  TEXT,
    country_name  TEXT,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- MATCH_COACHES  (who managed which team in which match)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS match_coaches (
    match_id   INTEGER NOT NULL,
    team_id    INTEGER NOT NULL,
    coach_id   INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (match_id, team_id),
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (team_id)  REFERENCES teams(id),
    FOREIGN KEY (coach_id) REFERENCES coaches(id)
);

-- -----------------------------------------------------------------------------
-- MATCH_MOMENTUM  (minute-by-minute momentum swing, -100..100; positive = home.
-- minute is REAL: FotMob uses 45.5 / 90.5 for stoppage-time points.)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS match_momentum (
    match_id   INTEGER NOT NULL,
    minute     REAL NOT NULL,
    value      REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (match_id, minute),
    FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- =============================================================================
-- INDEXES  (FKs + common filter columns)
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_seasons_league            ON seasons(league_id);
CREATE INDEX IF NOT EXISTS idx_team_seasons_team         ON team_seasons(team_id);
CREATE INDEX IF NOT EXISTS idx_player_seasons_player     ON player_seasons(player_id);
CREATE INDEX IF NOT EXISTS idx_player_seasons_team       ON player_seasons(team_id);
CREATE INDEX IF NOT EXISTS idx_matches_season            ON matches(season_id);
CREATE INDEX IF NOT EXISTS idx_matches_home_team         ON matches(home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_team         ON matches(away_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_kickoff           ON matches(kickoff_time_utc);
CREATE INDEX IF NOT EXISTS idx_matches_season_status     ON matches(season_id, status);
CREATE INDEX IF NOT EXISTS idx_mts_team                  ON match_team_stats(team_id, period);
CREATE INDEX IF NOT EXISTS idx_appearances_player        ON appearances(player_id);
CREATE INDEX IF NOT EXISTS idx_appearances_team          ON appearances(team_id);
CREATE INDEX IF NOT EXISTS idx_events_match              ON match_events(match_id);
CREATE INDEX IF NOT EXISTS idx_events_player             ON match_events(player_id);
CREATE INDEX IF NOT EXISTS idx_events_team               ON match_events(team_id);
CREATE INDEX IF NOT EXISTS idx_shots_match               ON shots(match_id);
CREATE INDEX IF NOT EXISTS idx_shots_player              ON shots(player_id);
CREATE INDEX IF NOT EXISTS idx_shots_team                ON shots(team_id);
CREATE INDEX IF NOT EXISTS idx_awards_season             ON season_awards(season_id);
CREATE INDEX IF NOT EXISTS idx_awards_player             ON season_awards(player_id);
CREATE INDEX IF NOT EXISTS idx_squads_season             ON season_squads(season_id);
CREATE INDEX IF NOT EXISTS idx_squad_players_player      ON season_squad_players(player_id);
CREATE INDEX IF NOT EXISTS idx_match_coaches_coach       ON match_coaches(coach_id);

-- =============================================================================
-- VIEWS  (the agent-facing query surface)
-- =============================================================================

-- One row per team per match (FULL-MATCH stats only, period='All'):
-- opponent, venue, result, and stats. The workhorse for team form/analytics.
CREATE VIEW IF NOT EXISTS v_team_match AS
SELECT
    mts.match_id,
    m.season_id,
    m.kickoff_time_utc,
    mts.team_id,
    t.name              AS team_name,
    CASE WHEN mts.is_home THEN m.away_team_id ELSE m.home_team_id END AS opponent_id,
    opp.name            AS opponent_name,
    mts.is_home,
    CASE WHEN mts.is_home THEN m.home_score ELSE m.away_score END AS goals_for,
    CASE WHEN mts.is_home THEN m.away_score ELSE m.home_score END AS goals_against,
    CASE
        WHEN m.winner_team_id IS NULL THEN 'D'
        WHEN m.winner_team_id = mts.team_id THEN 'W'
        ELSE 'L'
    END                 AS result,
    mts.formation, mts.xg, mts.xgot, mts.shots, mts.shots_on_target,
    mts.big_chances, mts.possession_pct, mts.pass_accuracy_pct, mts.corners,
    mts.tackles, mts.interceptions, mts.saves, mts.yellow_cards, mts.red_cards
FROM match_team_stats mts
JOIN matches m  ON m.id = mts.match_id
JOIN teams   t  ON t.id = mts.team_id
JOIN teams   opp ON opp.id = CASE WHEN mts.is_home THEN m.away_team_id ELSE m.home_team_id END
WHERE mts.period = 'All';

-- Period-aware variant for half-by-half analysis. One row per team per match
-- per period. REMEMBER: 'All' duplicates the halves — filter or group by
-- period, never SUM across all rows of this view.
CREATE VIEW IF NOT EXISTS v_team_period AS
SELECT
    mts.match_id,
    m.season_id,
    m.kickoff_time_utc,
    mts.period,
    mts.team_id,
    t.name              AS team_name,
    CASE WHEN mts.is_home THEN m.away_team_id ELSE m.home_team_id END AS opponent_id,
    opp.name            AS opponent_name,
    mts.is_home,
    mts.xg, mts.xgot, mts.shots, mts.shots_on_target, mts.big_chances,
    mts.possession_pct, mts.pass_accuracy_pct, mts.corners,
    mts.tackles, mts.interceptions, mts.saves, mts.yellow_cards, mts.red_cards
FROM match_team_stats mts
JOIN matches m  ON m.id = mts.match_id
JOIN teams   t  ON t.id = mts.team_id
JOIN teams   opp ON opp.id = CASE WHEN mts.is_home THEN m.away_team_id ELSE m.home_team_id END;

-- Both teams side by side for a single match (the old wide shape, on demand).
CREATE VIEW IF NOT EXISTS match_full AS
SELECT
    m.*,
    h.formation AS home_formation, a.formation AS away_formation,
    h.xg AS home_xg, a.xg AS away_xg,
    h.xgot AS home_xgot, a.xgot AS away_xgot,
    h.shots AS home_shots, a.shots AS away_shots,
    h.shots_on_target AS home_shots_on_target, a.shots_on_target AS away_shots_on_target,
    h.possession_pct AS home_possession_pct, a.possession_pct AS away_possession_pct,
    h.corners AS home_corners, a.corners AS away_corners,
    w.temperature, w.description AS weather_description
FROM matches m
JOIN match_team_stats h ON h.match_id = m.id AND h.is_home = 1 AND h.period = 'All'
JOIN match_team_stats a ON a.match_id = m.id AND a.is_home = 0 AND a.period = 'All'
LEFT JOIN match_weather w ON w.match_id = m.id;

-- Appearances enriched with names + match context.
CREATE VIEW IF NOT EXISTS v_player_match AS
SELECT
    ap.match_id, ap.player_id, p.name AS player_name,
    ap.team_id, t.name AS team_name,
    m.season_id, m.kickoff_time_utc,
    CASE WHEN m.home_team_id = ap.team_id THEN m.away_team_id ELSE m.home_team_id END AS opponent_id,
    (m.home_team_id = ap.team_id) AS is_home,
    ap.position, ap.minutes_played, ap.rating,
    ap.goals, ap.assists, ap.xg, ap.xa, ap.shots, ap.chances_created
FROM appearances ap
JOIN players p ON p.id = ap.player_id
JOIN teams   t ON t.id = ap.team_id
JOIN matches m ON m.id = ap.match_id;

-- Season player totals with names (cache table + labels).
CREATE VIEW IF NOT EXISTS v_player_season AS
SELECT
    ps.season_id, s.name AS season_name,
    ps.player_id, p.name AS player_name, p.primary_position,
    ps.team_id, t.name AS team_name,
    ps.appearances, ps.minutes_played, ps.goals, ps.assists,
    ps.goal_contributions, ps.xg, ps.xa, ps.average_rating
FROM player_seasons ps
JOIN players p ON p.id = ps.player_id
JOIN teams   t ON t.id = ps.team_id
JOIN seasons s ON s.id = ps.season_id;

-- League table with team + league/season labels.
CREATE VIEW IF NOT EXISTS v_standings AS
SELECT
    ts.season_id, s.name AS season_name, l.name AS league_name,
    ts.position, ts.team_id, t.name AS team_name,
    ts.played, ts.wins, ts.draws, ts.losses,
    ts.goals_for, ts.goals_against, ts.goal_difference, ts.points, ts.form
FROM team_seasons ts
JOIN teams   t ON t.id = ts.team_id
JOIN seasons s ON s.id = ts.season_id
JOIN leagues l ON l.id = s.league_id;