"""Validated persistence and CRUD for editable camera zones."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal
from utils.config_loader import load_json, save_json, CONFIG_DIR

ZoneType = Literal["no_parking_zones", "free_left_zones", "stop_lines", "signal_rois"]
@dataclass
class Zone:
    id: str; name: str; points: list[list[int]] | None = None
    x: int | None = None; y: int | None = None; width: int | None = None; height: int | None = None

class ZoneManager:
    def __init__(self, path: Path | None = None):
        self.path = path or CONFIG_DIR / "zones.json"; self.data = load_json(self.path, self._empty("CAM_01"))
        self._normalise()
    @staticmethod
    def _empty(camera_id: str) -> dict:
        return {"camera_id": camera_id, "no_parking_zones": [], "free_left_zones": [], "stop_lines": [], "signal_rois": []}
    def _normalise(self) -> None:
        for key in self._empty(""):
            self.data.setdefault(key, [] if key != "camera_id" else "CAM_01")
    def list(self, kind: ZoneType) -> list[dict]: return self.data[kind]
    def add(self, kind: ZoneType, zone: Zone) -> None:
        self._validate(kind, zone); self.data[kind].append({k:v for k,v in asdict(zone).items() if v is not None})
    def remove(self, kind: ZoneType, zone_id: str) -> None:
        self.data[kind] = [z for z in self.data[kind] if z.get("id") != zone_id]
    def clear(self) -> None:
        for kind in self._empty(""):
            if kind != "camera_id": self.data[kind] = []
    def save(self) -> None: save_json(self.path, self.data)
    def _validate(self, kind: ZoneType, zone: Zone) -> None:
        if kind == "stop_lines" and (not zone.points or len(zone.points) != 2): raise ValueError("A stop line needs exactly two points")
        if kind in ("no_parking_zones", "free_left_zones") and (not zone.points or len(zone.points) < 3): raise ValueError("A polygon needs at least three points")
        if kind == "signal_rois" and (not zone.width or not zone.height): raise ValueError("Signal ROI needs non-zero width and height")
