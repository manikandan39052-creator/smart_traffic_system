"""Lazy YOLO adapter; the application remains usable without model packages."""
from __future__ import annotations
import logging
import numpy as np
from detection.detection_types import Detection
log = logging.getLogger(__name__)
VEHICLES = {1:"bicycle", 2:"car", 3:"motorcycle", 5:"bus", 7:"truck"}
class VehicleDetector:
    def __init__(self, model_path: str, confidence: float = .4):
        self.confidence = confidence; self.model = None
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
        except Exception as exc: log.warning("YOLO unavailable; detection disabled: %s", exc)
    def detect(self, frame: np.ndarray) -> list[Detection]:
        if self.model is None: return []
        result = self.model(frame, conf=self.confidence, verbose=False)[0]; out=[]
        for box in result.boxes:
            cls = int(box.cls[0]);
            if cls in VEHICLES: out.append(Detection(tuple(map(float, box.xyxy[0])), VEHICLES[cls], float(box.conf[0])))
        return out
