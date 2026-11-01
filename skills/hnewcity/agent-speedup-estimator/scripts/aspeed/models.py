from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Event:
    start: float
    end: float
    kind: str
    category: str
    family: str = ""
    interrupted: bool = False

    @property
    def wall(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class SessionTiming:
    agent: str
    session: str
    model_s: float = 0.0
    human_s: float = 0.0
    idle_s: float = 0.0
    background_s: float = 0.0
    stalled_s: float = 0.0
    first_ts: Optional[float] = None
    last_ts: Optional[float] = None
    events: List[Event] = field(default_factory=list)

    def touch(self, ts: float) -> None:
        if self.first_ts is None or ts < self.first_ts:
            self.first_ts = ts
        if self.last_ts is None or ts > self.last_ts:
            self.last_ts = ts
