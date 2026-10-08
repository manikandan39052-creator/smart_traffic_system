"""Lightweight IoU tracker; replaceable by YOLO ByteTrack when configured."""
from __future__ import annotations
from datetime import datetime
from detection.detection_types import Detection, Track
from zones.geometry import bottom_center
class SimpleTracker:
    def __init__(self, max_missed: int = 20): self.tracks={}; self.missed={}; self.next_id=1; self.max_missed=max_missed
    @staticmethod
    def _iou(a,b):
        x1,y1=max(a[0],b[0]),max(a[1],b[1]); x3,y3=min(a[2],b[2]),min(a[3],b[3])
        inter=max(0,x3-x1)*max(0,y3-y1); area=lambda q:max(0,q[2]-q[0])*max(0,q[3]-q[1]); return inter/(area(a)+area(b)-inter+1e-9)
    def update(self, detections: list[Detection]) -> list[Track]:
        unmatched=set(self.tracks); result=[]
        for det in detections:
            candidates=[(self._iou(det.box,t.box), tid) for tid,t in self.tracks.items() if t.label==det.label]
            score,tid=max(candidates, default=(0,None))
            if score < .25:
                tid=self.next_id; self.next_id+=1; self.tracks[tid]=Track(tid,det.label,det.box,det.confidence)
            t=self.tracks[tid]; t.previous_position=t.trajectory[-1] if t.trajectory else None; t.box=det.box; t.confidence=det.confidence; t.last_seen=datetime.now(); t.trajectory.append(bottom_center(det.box)); t.trajectory=t.trajectory[-100:]; det.track_id=tid; self.missed[tid]=0; unmatched.discard(tid); result.append(t)
        for tid in unmatched: self.missed[tid]=self.missed.get(tid,0)+1
        for tid in [x for x,n in self.missed.items() if n>self.max_missed]: self.tracks.pop(tid,None); self.missed.pop(tid,None)
        return result
