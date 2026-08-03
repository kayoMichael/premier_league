from premier_league.base import BaseDataSetScrapper
from premier_league.utils.url import MatchUrl, MATCH_STATISTICS_LEAGUE
from premier_league.utils.methods import current_season
from premier_league.utils.xpath import MATCHES, XPathElement
from premier_league.data.cls.match_record import MatchRecord
from premier_league.data.cls.shot_record import ShotRecord
from premier_league.data.cls.player_record import PlayerRecord
from premier_league.data.cls.match_coach_record import MatchCoachRecord
from premier_league.data.cls.team_stats_record import TeamStatsRecord
from premier_league.data.cls.appearance_record import AppearanceRecord
from premier_league.data.cls.event_record import EventRecord
from premier_league.data.cls.momentum_record import MomentumRecord
from premier_league.data.cls.match_bundle import MatchBundle
from premier_league.match_statistics.utils.helper import _int, _get, stat_value, stat_total, split_pct, to_num, _pct_ratio
from premier_league.match_statistics.utils.map import TEAM_STAT_MAP, TEAM_FRACTION_MAP, TEAM_IGNORED, SHOT_OUTCOME, BODY_PART, PLAYER_IGNORED, PLAYER_FRACTION_MAP, PLAYER_STAT_MAP

import sqlite3

from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import json, time

OUT = Path("matches")
OUT.mkdir(exist_ok=True)

class MatchPipeline(BaseDataSetScrapper):
    def __init__(self, db_name="matches.db"):
        super().__init__()
        self.matches = None
        self.conn = sqlite3.connect(db_name)

    def process_data(self):
        urls = []
        curr_season = current_season()
        for league in MATCH_STATISTICS_LEAGUE:
            for year in range(2016, curr_season + 1):
                season = str(year) if league == "mls" else f"{year}-{year + 1}"

                url = MatchUrl.get(
                    league=league,
                    page_type="fixtures",
                )

                urls.append(f"{url}?season={season}&page=9999&group=by-date")

        self.scrape_and_process_all(urls, rate_limit=4, return_html=False, process_func=self.extract_all_url)

        urls = []
        for league in MATCH_STATISTICS_LEAGUE:
            for year in range(2016, curr_season + 1):
                season = str(year) if league == "mls" else f"{year}-{year + 1}"
                urls.extend([f"{MatchUrl.get(
                    league=league,
                    page_type="overview"
                )}?season={season}", f"{MatchUrl.get(
                    league=league,
                    page_type="stats"
                )}/players?season={season}", f"{MatchUrl.get(
                    league=league,
                    page_type="overview"
                )}/teams?season={season}"])

        self.scrape_and_process_all(urls, rate_limit=4, return_html=False)

    def extract_all_url(self, root: XPathElement, url: str):
        script = root.xpath(MATCHES.MATCH_URLS)[0]

        data = json.loads(script)

        fixtures = data["props"]["pageProps"]["fixtures"]["allMatches"]
        import pdb; pdb.set_trace()
        self.matches = [(int(m["id"]), m["pageUrl"]) for m in fixtures]
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            for mid, pageUrl in self.matches:
                out_file = OUT / f"{mid}.json"
                if out_file.exists():
                    continue

                try:
                    with page.expect_response(lambda r, mid=mid: "matchDetails" in r.url and f"matchId={mid}" in r.url
                                                                 and r.status == 200,
                                              timeout=20000) as resp_info:
                        page.goto(f"https://www.fotmob.com{pageUrl}",
                                  wait_until="domcontentloaded")

                    data = resp_info.value.json()
                    got_id = str(data.get("general", {}).get("matchId"))
                    if data.get("error") or got_id != str(mid):
                        print(f"bad payload for {mid}: {data.get('message')}")
                        continue

                    out_file.write_text(json.dumps(data, indent=2))
                    print(f"saved {mid}: {data['general']['matchName']}")
                    time.sleep(4)
                except PWTimeout:
                    print(f"timeout on {mid}, skipping")
                    continue


    def insert_into_db(self, season):
        for mid, pageUrl in self.matches:
            out_file = OUT / f"{mid}.json"
            if not out_file.exists():
                continue

            with out_file.open() as f:
                data = json.load(f)

    @staticmethod
    def _parse_match(data: dict, bundle: MatchBundle) -> MatchRecord:
        g = data.get("general") or {}
        status = _get(data, "header", "status", default={}) or {}
        info = _get(data, "content", "matchFacts", "infoBox", default={}) or {}

        m = MatchRecord(
            id=_int(g.get("matchId")),
            league_id=_int(g.get("leagueId")),
            parent_league_id=_int(g.get("parentLeagueId")),
            league_name=g.get("leagueName"),
            home_team_id=_int(_get(g, "homeTeam", "id")),
            away_team_id=_int(_get(g, "awayTeam", "id")),
            home_team_name=_get(g, "homeTeam", "name"),
            away_team_name=_get(g, "awayTeam", "name"),
            match_name=g.get("matchName"),
            round=str(g.get("matchRound")) if g.get("matchRound") is not None else None,
            round_name=g.get("leagueRoundName"),
            kickoff_time_utc=g.get("matchTimeUTCDate"),
            status=_get(status, "reason", "long") or ("finished" if status.get("finished") else None),
            result_string=status.get("scoreStr"),
            finished=status.get("finished"),
            cancelled=status.get("cancelled"),
            coverage_level=g.get("coverageLevel"),
            referee_name=_get(info, "Referee", "text"),
            attendance=_int(info.get("Attendance")),
            stadium_name=_get(info, "Stadium", "name"),
            stadium_city=_get(info, "Stadium", "city"),
            stadium_country=_get(info, "Stadium", "country"),
            stadium_lat=to_num(_get(info, "Stadium", "lat")),
            stadium_long=to_num(_get(info, "Stadium", "long")),
            stadium_capacity=_int(_get(info, "Stadium", "capacity")),
            stadium_surface=_get(info, "Stadium", "surface"),
            highlights_url=_get(data, "content", "matchFacts", "highlights", "url"),
        )

        # scores: match header.teams to home/away by id, don't trust ordering
        for t in _get(data, "header", "teams", default=[]) or []:
            tid = _int(t.get("id"))
            if tid == m.home_team_id:
                m.home_score = _int(t.get("score"))
            elif tid == m.away_team_id:
                m.away_score = _int(t.get("score"))

        if m.finished and m.home_score is not None and m.away_score is not None:
            if m.home_score > m.away_score:
                m.winner_team_id = m.home_team_id
            elif m.away_score > m.home_score:
                m.winner_team_id = m.away_team_id
        # penalties override (whoLostOnPenalties gives the loser)
        lost_pens = status.get("whoLostOnPenalties")
        if lost_pens:
            if lost_pens == m.home_team_name:
                m.winner_team_id = m.away_team_id
            elif lost_pens == m.away_team_name:
                m.winner_team_id = m.home_team_id

        # halftime from the "Half" timeline event marked HT
        for ev in _get(data, "content", "matchFacts", "events", "events", default=[]) or []:
            if ev.get("type") == "Half" and ev.get("halfStrShort") == "HT":
                m.home_halftime_score = _int(ev.get("homeScore"))
                m.away_halftime_score = _int(ev.get("awayScore"))
                break

        if m.id is None:
            bundle.warnings.append("general.matchId missing")
        return m

    @staticmethod
    def _parse_team_stats_period(period: str, groups: list, m: MatchRecord,
                                 bundle: MatchBundle) -> list[TeamStatsRecord]:
        pairs: dict[str, list] = {}
        for group in groups:
            for item in group.get("stats") or []:
                if item.get("type") == "title":
                    continue
                key = item.get("key")
                vals = item.get("stats")
                if key and isinstance(vals, list) and len(vals) == 2 and key not in pairs:
                    pairs[key] = vals
        if not pairs:
            return []

        home = TeamStatsRecord(match_id=m.id, team_id=m.home_team_id, period=period, is_home=True)
        away = TeamStatsRecord(match_id=m.id, team_id=m.away_team_id, period=period, is_home=False)

        for key, (hv, av) in pairs.items():
            if key in TEAM_FRACTION_MAP:
                count_col, pct_col = TEAM_FRACTION_MAP[key]
                for rec, v in ((home, hv), (away, av)):
                    cnt, pct = split_pct(v)
                    setattr(rec, count_col, _int(cnt))
                    if pct_col:
                        setattr(rec, pct_col, pct)
            elif key in TEAM_STAT_MAP:
                col = TEAM_STAT_MAP[key]
                for rec, v in ((home, hv), (away, av)):
                    n = to_num(v)
                    setattr(rec, col, n)
            elif key not in TEAM_IGNORED:
                bundle.unmapped_keys.add(f"team:{key}")

        # derive pass accuracy if missing but counts present
        for rec in (home, away):
            if rec.pass_accuracy_pct is None:
                rec.pass_accuracy_pct = _pct_ratio(rec.accurate_passes, rec.total_passes)
        return [home, away]

    def _parse_team_stats(self, data: dict, m: MatchRecord, bundle: MatchBundle) -> list[TeamStatsRecord]:
        """One home+away pair per period FotMob provides ('All', 'FirstHalf',
        'SecondHalf', extra-time keys in cup games). Iterated dynamically so new
        period names flow through without a code change."""
        periods = _get(data, "content", "stats", "Periods", default={}) or {}
        out: list[TeamStatsRecord] = []
        for period, block in periods.items():
            groups = (block or {}).get("stats") or []
            out.extend(self._parse_team_stats_period(period, groups, m, bundle))

        if not any(r.period == "All" for r in out):
            bundle.warnings.append("no team stats (content.stats.Periods.All empty — low coverage?)")

        # formations are full-match facts -> attach to the 'All' rows only
        for rec in out:
            if rec.period == "All":
                side = "homeTeam" if rec.is_home else "awayTeam"
                rec.formation = _get(data, "content", "lineup", side, "formation")
        return out

    @staticmethod
    def _lineup_index(data: dict) -> dict[int, dict]:
        """player_id -> {is_starter, shirt_number, minute_entered, minute_left, potm}"""
        out: dict[int, dict] = {}
        lineup = _get(data, "content", "lineup", default={}) or {}
        for side in ("homeTeam", "awayTeam"):
            team = lineup.get(side) or {}
            for group, is_starter in (("starters", True), ("subs", False)):
                for p in team.get(group) or []:
                    pid = _int(p.get("id"))
                    if pid is None:
                        continue
                    perf = p.get("performance") or {}
                    entry = {
                        "is_starter": is_starter,
                        "shirt_number": _int(p.get("shirtNumber")),
                        "minute_entered": 0 if is_starter else None,
                        "minute_left": None,
                        "potm": bool(perf.get("playerOfTheMatch")),
                        # master-data enrichment carried through to records
                        "first_name": p.get("firstName") or None,
                        "last_name": p.get("lastName") or None,
                        "country_name": p.get("countryName"),
                        "country_code": p.get("countryCode"),
                        "market_value": _int(p.get("marketValue")),
                        "age": _int(p.get("age")),
                    }
                    for se in perf.get("substitutionEvents") or []:
                        if se.get("type") == "subIn":
                            entry["minute_entered"] = _int(se.get("time"))
                        elif se.get("type") == "subOut":
                            entry["minute_left"] = _int(se.get("time"))
                    out[pid] = entry
        return out

    def _parse_appearances(self, data: dict, m: MatchRecord, bundle: MatchBundle) -> list[AppearanceRecord]:
        pstats = _get(data, "content", "playerStats", default={}) or {}
        lineup = self._lineup_index(data)
        out: list[AppearanceRecord] = []

        for pid_str, p in pstats.items():
            pid = _int(p.get("id")) or _int(pid_str)
            rec = AppearanceRecord(
                match_id=m.id,
                player_id=pid,
                player_name=p.get("name"),
                team_id=_int(p.get("teamId")),
                player_of_match=bool(p.get("isPotm")) or None,
            )

            li = lineup.get(pid)
            if li:
                rec.is_starter = li["is_starter"]
                rec.is_substitute = not li["is_starter"]
                rec.shirt_number = li["shirt_number"]
                rec.minute_entered = li["minute_entered"]
                rec.minute_left = li["minute_left"]
                rec.market_value = li["market_value"]
                rec.age_at_match = li["age"]
                if li["potm"]:
                    rec.player_of_match = True

            # flatten stat groups into key -> stat_obj (first occurrence wins)
            flat: dict[str, dict] = {}
            for group in p.get("stats") or []:
                for label, obj in (group.get("stats") or {}).items():
                    if not isinstance(obj, dict):
                        continue
                    key = obj.get("key") or label
                    flat.setdefault(key, obj)

            # unused-sub rows have stats: [] — keep the row (lineup info) but no stats
            for key, obj in flat.items():
                if key in PLAYER_FRACTION_MAP:
                    v_col, t_col, pct_col = PLAYER_FRACTION_MAP[key]
                    setattr(rec, v_col, _int(stat_value(obj)))
                    setattr(rec, t_col, _int(stat_total(obj)))
                    if pct_col:
                        setattr(rec, pct_col, _pct_ratio(stat_value(obj), stat_total(obj)))
                elif key in PLAYER_STAT_MAP:
                    col, caster = PLAYER_STAT_MAP[key]
                    v = stat_value(obj)  # may be absent entirely -> None
                    n = to_num(v)
                    if n is not None:
                        setattr(rec, col, caster(n))
                elif key not in PLAYER_IGNORED:
                    bundle.unmapped_keys.add(f"player:{key}")

            # duels_attempted = won + lost (lost isn't stored on its own)
            lost = to_num(stat_value(flat.get("duel_lost")))
            if rec.duels_won is not None and lost is not None:
                rec.duels_attempted = rec.duels_won + int(lost)

            # keeper clean sheet, only when we actually know goals_conceded
            if p.get("isGoalkeeper") and rec.goals_conceded is not None:
                rec.clean_sheet = rec.goals_conceded == 0

            out.append(rec)
        return out

    @staticmethod
    def _parse_events(data: dict, m: MatchRecord, bundle: MatchBundle) -> list[EventRecord]:
        events = _get(data, "content", "matchFacts", "events", "events", default=[]) or []
        out: list[EventRecord] = []
        for i, ev in enumerate(events):
            etype = ev.get("type")
            if etype == "Half":
                continue  # period markers, not events
            rec = EventRecord(
                match_id=m.id,
                fotmob_event_id=_int(ev.get("eventId")),
                minute=_int(ev.get("time")),
                added_time=_int(ev.get("overloadTime")),
                event_type=(etype or "").lower() or None,
                event_type_raw=etype,
                is_home=ev.get("isHome"),
                home_score=_int(ev.get("homeScore")),
                away_score=_int(ev.get("awayScore")),
                sort_order=i,
            )
            if rec.is_home is True:
                rec.team_id = m.home_team_id
            elif rec.is_home is False:
                rec.team_id = m.away_team_id

            pid = _get(ev, "player", "id")
            rec.player_id = _int(pid)

            if etype == "Goal":
                rec.is_goal = True
                rec.is_own_goal = bool(ev.get("ownGoal"))
                rec.is_penalty = ev.get("goalDescriptionKey") == "penalty"
                rec.is_penalty_shootout = bool(ev.get("isPenaltyShootoutEvent"))
                rec.event_description = ev.get("goalDescription")
                new_score = ev.get("newScore")
                if isinstance(new_score, list) and len(new_score) == 2:
                    rec.home_score = _int(new_score[0])
                    rec.away_score = _int(new_score[1])
            elif etype == "Card":
                rec.card_type = ev.get("card")
            elif etype == "Substitution":
                swap = ev.get("swap") or []
                # swap[0] = player coming ON, swap[1] = player going OFF
                if len(swap) >= 1:
                    rec.player_id = _int(_get(swap[0], "id"))
                if len(swap) >= 2:
                    rec.related_player_id = _int(_get(swap[1], "id"))

            out.append(rec)
        return out

    @staticmethod
    def _parse_shots(data: dict, m: MatchRecord, bundle: MatchBundle) -> list[ShotRecord]:
        shots = _get(data, "content", "shotmap", "shots", default=[]) or []
        out: list[ShotRecord] = []
        for s in shots:
            on_goal = s.get("onGoalShot") or {}
            etype = s.get("eventType")
            if etype in SHOT_OUTCOME:
                outcome = SHOT_OUTCOME[etype]
            elif etype == "AttemptSaved":
                outcome = "Blocked" if s.get("isBlocked") else "Saved"
            else:
                outcome = etype  # unknown future type: pass through raw
            out.append(ShotRecord(
                match_id=m.id,
                fotmob_shot_id=_int(s.get("id")),
                outcome=outcome,
                body_part=BODY_PART.get(s.get("shotType"),
                                        "Other" if s.get("shotType") else None),
                is_saved=(etype == "AttemptSaved" and not s.get("isBlocked")),
                is_from_inside_box=s.get("isFromInsideBox"),
                is_saved_off_line=s.get("isSavedOffLine"),
                team_id=_int(s.get("teamId")),
                player_id=_int(s.get("playerId")),
                keeper_id=_int(s.get("keeperId")),
                minute=_int(s.get("min")),
                added_time=_int(s.get("minAdded")),
                period=s.get("period"),
                event_type_raw=s.get("eventType"),
                shot_type=s.get("shotType"),
                situation=s.get("situation"),
                x=to_num(s.get("x")),
                y=to_num(s.get("y")),
                blocked_x=to_num(s.get("blockedX")),
                blocked_y=to_num(s.get("blockedY")),
                goal_crossed_y=to_num(s.get("goalCrossedY")),
                goal_crossed_z=to_num(s.get("goalCrossedZ")),
                on_goal_x=to_num(on_goal.get("x")),
                on_goal_y=to_num(on_goal.get("y")),
                on_goal_zoom_ratio=to_num(on_goal.get("zoomRatio")),
                xg=to_num(s.get("expectedGoals")),
                xgot=to_num(s.get("expectedGoalsOnTarget")),
                is_goal=s.get("eventType") == "Goal",
                is_own_goal=s.get("isOwnGoal"),
                is_big_chance=s.get("isBigChance"),
                is_blocked=s.get("isBlocked"),
                is_on_target=s.get("isOnTarget"),
                is_from_penalty=s.get("situation") == "Penalty",
                is_header=s.get("shotType") == "Header",
            ))
        if not shots:
            bundle.warnings.append("no shotmap (pre-xG season or low coverage)")
        return out

    @staticmethod
    def _parse_players(self, data: dict, bundle: MatchBundle) -> list[PlayerRecord]:
        """Master-data for the players upsert: names + optaId from playerStats,
        nationality/full names from the lineup block."""
        pstats = _get(data, "content", "playerStats", default={}) or {}
        lineup = self._lineup_index(data)
        out: list[PlayerRecord] = []
        for pid_str, p in pstats.items():
            pid = _int(p.get("id")) or _int(pid_str)
            if pid is None:
                continue
            li = lineup.get(pid) or {}
            out.append(PlayerRecord(
                id=pid,
                name=p.get("name"),
                first_name=li.get("first_name"),
                last_name=li.get("last_name"),
                nationality=li.get("country_name"),
                country_code=li.get("country_code"),
                opta_id=str(p["optaId"]) if p.get("optaId") is not None else None,
                is_goalkeeper=p.get("isGoalkeeper"),
            ))
        return out

    @staticmethod
    def _parse_coaches(data: dict, m: MatchRecord, bundle: MatchBundle) -> list[MatchCoachRecord]:
        out: list[MatchCoachRecord] = []
        for side, team_id in (("homeTeam", m.home_team_id), ("awayTeam", m.away_team_id)):
            c = _get(data, "content", "lineup", side, "coach", default=None)
            if not isinstance(c, dict) or c.get("id") is None:
                continue
            out.append(MatchCoachRecord(
                match_id=m.id,
                team_id=team_id,
                coach_id=_int(c.get("id")),
                name=c.get("name"),
                first_name=c.get("firstName") or None,
                last_name=c.get("lastName") or None,
                country_code=c.get("countryCode"),
                country_name=c.get("countryName"),
            ))
        return out

    @staticmethod
    def _parse_momentum(data: dict, m: MatchRecord, bundle: MatchBundle) -> list[MomentumRecord]:
        points = (_get(data, "content", "momentum", "main", "data")
                  or _get(data, "content", "matchFacts", "momentum", "main", "data")
                  or [])
        out: list[MomentumRecord] = []
        seen: set[float] = set()
        for pt in points:
            minute = to_num(pt.get("minute")) if isinstance(pt, dict) else None
            if minute is None or minute in seen:
                continue
            seen.add(minute)
            out.append(MomentumRecord(match_id=m.id, minute=minute,
                                      value=to_num(pt.get("value"))))
        return out


if __name__ == '__main__':
    scraper = MatchPipeline()
    scraper.process_data()