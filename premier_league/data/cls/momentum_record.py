from dataclasses import dataclass
from typing import Optional

@dataclass
class MomentumRecord:
    match_id: Optional[int] = None
    minute: Optional[float] = None           # REAL: 45.5 / 90.5 = stoppage time
    value: Optional[float] = None            # -100..100, positive = home