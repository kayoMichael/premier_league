import re
from typing import Any, Optional

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