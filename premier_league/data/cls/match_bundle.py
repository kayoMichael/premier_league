from dataclasses import dataclass, field
from premier_league.data.cls.match_record import MatchRecord
from premier_league.data.cls.shot_record import ShotRecord
from premier_league.data.cls.player_record import PlayerRecord
from premier_league.data.cls.match_coach_record import MatchCoachRecord
from premier_league.data.cls.team_stats_record import TeamStatsRecord
from premier_league.data.cls.appearance_record import AppearanceRecord
from premier_league.data.cls.event_record import EventRecord
from premier_league.data.cls.momentum_record import MomentumRecord

@dataclass
class MatchBundle:
    match: MatchRecord
    team_stats: list[TeamStatsRecord] = field(default_factory=list)
    appearances: list[AppearanceRecord] = field(default_factory=list)
    events: list[EventRecord] = field(default_factory=list)
    shots: list[ShotRecord] = field(default_factory=list)
    players: list[PlayerRecord] = field(default_factory=list)
    coaches: list[MatchCoachRecord] = field(default_factory=list)
    momentum: list[MomentumRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unmapped_keys: set[str] = field(default_factory=set)

    def summary(self) -> str:
        m = self.match
        return (f"[{m.id}] {m.match_name or '?'} | teams:{len(self.team_stats)} "
                f"apps:{len(self.appearances)} events:{len(self.events)} "
                f"shots:{len(self.shots)} warnings:{len(self.warnings)}")

    def validate(self) -> list[str]:
        """Structural invariants that must hold before insert. Everything is
        Optional at parse time so a weird payload never crashes the batch;
        THIS is where identity gets enforced. Empty list = insertable.
        Child rows missing identity are dropped (with an error noting it)
        rather than poisoning the whole bundle."""
        errors: list[str] = []
        m = self.match
        if m.id is None:
            errors.append("match.id missing — bundle not insertable")
        if m.home_team_id is None or m.away_team_id is None:
            errors.append("match home/away team id missing — bundle not insertable")

        def keep(rows, cond, label):
            bad = [r for r in rows if not cond(r)]
            if bad:
                errors.append(f"dropped {len(bad)} {label} row(s) missing identity")
            return [r for r in rows if cond(r)]

        self.team_stats = keep(self.team_stats,
                               lambda t: t.team_id is not None and t.is_home is not None,
                               "team_stats")
        self.appearances = keep(self.appearances,
                                lambda a: a.player_id is not None and a.team_id is not None,
                                "appearance")
        self.shots = keep(self.shots, lambda s: s.match_id is not None, "shot")
        return errors

    @property
    def is_insertable(self) -> bool:
        return self.match.id is not None and \
            self.match.home_team_id is not None and \
            self.match.away_team_id is not None