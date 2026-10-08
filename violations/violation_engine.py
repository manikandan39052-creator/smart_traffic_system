"""Coordinates zone rules and returns one-shot violation commands."""
from __future__ import annotations
from dataclasses import dataclass
from detection.detection_types import Track
from zones.geometry import point_in_polygon
from violations.no_parking import NoParkingRule
from violations.stop_line import StopLineRule
from violations.free_left import FreeLeftRule
@dataclass
class ViolationEvent: track_id:int; violation_type:str; zone_id:str; duration:float=0
class ViolationEngine:
    def __init__(self, grace=10, post_alarm=5): self.parking=NoParkingRule(grace,post_alarm); self.stop=StopLineRule(); self.free_left=FreeLeftRule()
    def evaluate(self, track: Track, zones: dict, signal_state: str) -> list[ViolationEvent]:
        events=[]; pos=track.trajectory[-1]
        for z in zones["no_parking_zones"]:
            result=self.parking.update((track.track_id,z["id"]), point_in_polygon(pos,z["points"]))
            if result == "warning": events.append(ViolationEvent(track.track_id,"NO_PARKING_WARNING",z["id"]))
            elif result == "confirmed": events.append(ViolationEvent(track.track_id,"NO_PARKING",z["id"]))
        for z in zones["stop_lines"]:
            if self.stop.check(track.track_id,track.previous_position,pos,z["points"],signal_state): events.append(ViolationEvent(track.track_id,"RED_LIGHT",z["id"]))
        for z in zones["free_left_zones"]:
            if self.free_left.check(track.track_id,pos,z["id"],z["points"]): events.append(ViolationEvent(track.track_id,"FREE_LEFT",z["id"]))
        return events
