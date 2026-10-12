from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherRecord:
    """Match-day weather from content.weather (1:1 optional with a match).

    FotMob proxies weather.com. Only populated from 2025 onward — the provider
    does not backfill history, so ~91% of matches have no weather at all.
    Field names mirror match_weather columns exactly: insert_bundle() feeds
    asdict() straight in as column names."""
    match_id: Optional[int] = None
    temperature: Optional[float] = None      # Celsius; arrives int, REAL in schema
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None     # cardinal, e.g. "SW"; absent on 106 rows
    icon_code: Optional[int] = None          # weather.com code; odd/even = night/day
    humidity_pct: Optional[float] = None
    precipitation: Optional[float] = None    # genuinely fractional (0 .. 16.51)
    snow: Optional[float] = None             # genuinely fractional (0 .. 0.8)
    cloud_cover_pct: Optional[float] = None
    description: Optional[str] = None        # raw provider text — messy, don't group on it
    localized_key: Optional[str] = None      # normalized bucket; NULL on 236 rows
    default_title: Optional[str] = None      # normalized bucket; NULL on 236 rows
    last_updated: Optional[str] = None       # ISO-8601; provenance — proves match-day reading
