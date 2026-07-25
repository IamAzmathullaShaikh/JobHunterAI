from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LocationDTO:
    city: str
    country: str
    state: Optional[str] = None
    is_remote: bool = False
