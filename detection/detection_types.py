from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Detection:
    box: tuple[float,float,float,float]; label: str; confidence: float; track_id: int | None = None
@dataclass
class Track:
    track_id: int; label: str; box: tuple[float,float,float,float]; confidence: float
    first_seen: datetime = field(default_factory=datetime.now); last_seen: datetime = field(default_factory=datetime.now)
    previous_position: tuple[float,float] | None = None; trajectory: list[tuple[float,float]] = field(default_factory=list)
