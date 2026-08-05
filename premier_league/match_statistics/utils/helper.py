import re
from typing import Any, Optional
from premier_league.data.cls.match_record import MatchRecord

MLS_CALENDAR_LEAGUES = {130, 10000002}   # MLS seasons are calendar years

_NUM_PCT = re.compile(r"^\s*(-?\d+(?:[.,]\d+)?)\s*(?:\(\s*(\d+(?:[.,]\d+)?)\s*%\s*\))?\s*$")


def to_num(v: Any) -> Optional[float]:
    """int/float pass through; '2.12' -> 2.12; '485 (87%)' -> 485; else None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        m = _NUM_PCT.match(v.replace(",", "."))
        if m:
            n = float(m.group(1))
            return int(n) if n.is_integer() else n
    return None


def split_pct(v: Any) -> tuple[Optional[float], Optional[float]]:
    """'485 (87%)' -> (485, 87.0). Plain number -> (n, None). Else (None, None)."""
    if isinstance(v, str):
        m = _NUM_PCT.match(v.replace(",", "."))
        if m:
            n = float(m.group(1))
            n = int(n) if n.is_integer() else n
            p = float(m.group(2)) if m.group(2) else None
            return n, p
    return to_num(v), None


def stat_value(stat_obj: Any) -> Any:
    """Inner value of a {'key':..,'stat':{'value':..}} object.
    The 'stat' dict sometimes has NO 'value' key at all -> None."""
    if not isinstance(stat_obj, dict):
        return None
    inner = stat_obj.get("stat")
    if not isinstance(inner, dict):
        return None
    return inner.get("value")


def stat_total(stat_obj: Any) -> Any:
    """'total' of a fractionWithPercentage stat (value/total)."""
    if not isinstance(stat_obj, dict):
        return None
    inner = stat_obj.get("stat")
    if not isinstance(inner, dict):
        return None
    return inner.get("total")


def _get(d: Any, *path, default=None):
    """Safe nested access: _get(data, 'content', 'stats', 'Periods')."""
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p)
    return cur if cur is not None else default


def _int(v: Any) -> Optional[int]:
    n = to_num(v)
    if n is None:
        return None
    try:
        return int(n)
    except (TypeError, ValueError):
        return None


def _pct_ratio(value, total) -> Optional[float]:
    v, t = to_num(value), to_num(total)
    if v is None or not t:
        return None
    return round(100.0 * v / t, 1)


def upsert(conn, table: str, row: dict, pk: tuple = ("id",), coalesce: bool = False):
    """INSERT .. ON CONFLICT DO UPDATE. Never DELETE+re-INSERT (unlike OR
    REPLACE), so FK children survive re-ingest. coalesce=True: only fill
    gaps, never overwrite an existing non-NULL value with NULL."""
    cols = ", ".join(row)
    ph = ", ".join(f":{c}" for c in row)
    if coalesce:
        sets = ", ".join(f"{c}=COALESCE(excluded.{c}, {c})" for c in row if c not in pk)
    else:
        sets = ", ".join(f"{c}=excluded.{c}" for c in row if c not in pk)
    conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({ph}) "
                 f"ON CONFLICT({', '.join(pk)}) DO UPDATE SET {sets}", row)


def replace_rows(conn, table: str, rows: list[dict]):
    """For NATURAL-composite-PK child tables only (match_team_stats,
    appearances, match_coaches, match_momentum) — OR REPLACE is idempotent
    there because re-ingest hits the same PK."""
    if not rows:
        return
    cols = ", ".join(rows[0])
    ph = ", ".join(f":{c}" for c in rows[0])
    conn.executemany(f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({ph})", rows)


def insert_rows(conn, table: str, rows: list[dict]):
    """Plain insert, for surrogate-PK tables AFTER a delete-by-match_id."""
    if not rows:
        return
    cols = ", ".join(rows[0])
    ph = ", ".join(f":{c}" for c in rows[0])
    conn.executemany(f"INSERT INTO {table} ({cols}) VALUES ({ph})", rows)


def season_name_for(m: MatchRecord) -> str:
    """'2024' for MLS-style calendar leagues, '2024-2025' for cross-year."""
    if not m.kickoff_time_utc:
        return "unknown"
    year, month = int(m.kickoff_time_utc[:4]), int(m.kickoff_time_utc[5:7])
    if m.league_id in MLS_CALENDAR_LEAGUES or m.parent_league_id in MLS_CALENDAR_LEAGUES:
        return str(year)
    start = year if month >= 7 else year - 1
    return f"{start}-{start + 1}"
