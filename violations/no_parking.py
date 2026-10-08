"""Temporal no-parking state machine with duplicate suppression."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from violations.state_manager import VehicleState

@dataclass
class ParkingState:
    entered_at: datetime; state: VehicleState = VehicleState.GRACE; warning_at: datetime | None = None; emitted: bool = False

class NoParkingRule:
    def __init__(self, grace_seconds: float=10, post_alarm_seconds: float=5): self.grace_seconds=grace_seconds; self.post_alarm_seconds=post_alarm_seconds; self.states={}
    def update(self, key: tuple[int,str], inside: bool, now: datetime | None=None) -> str | None:
        now=now or datetime.now()
        if not inside: self.states.pop(key, None); return None
        state=self.states.setdefault(key, ParkingState(now)); elapsed=(now-state.entered_at).total_seconds()
        if state.state == VehicleState.GRACE and elapsed >= self.grace_seconds:
            state.state=VehicleState.WARNING; state.warning_at=now; return "warning"
        if state.state == VehicleState.WARNING and (now-state.warning_at).total_seconds() >= self.post_alarm_seconds and not state.emitted:
            state.state=VehicleState.CONFIRMED; state.emitted=True; return "confirmed"
        return None
