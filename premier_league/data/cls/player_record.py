from dataclasses import dataclass
from typing import Optional

@dataclass
class PlayerRecord:
    """Master-data enrichment for the players table (upsert target)."""
    id: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nationality: Optional[str] = None
    country_code: Optional[str] = None
    opta_id: Optional[str] = None
    is_goalkeeper: Optional[bool] = None