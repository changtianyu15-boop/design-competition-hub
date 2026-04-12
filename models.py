from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class Competition:
    title: str
    competition_type: str
    deadline: str
    source_name: str
    source_url: str
    description: str = ""
    organizer: str = ""
    region: str = ""
    prize: str = ""
    fetched_at: str = ""

    def __post_init__(self) -> None:
        if not self.fetched_at:
            self.fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
