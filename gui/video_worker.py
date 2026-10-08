from __future__ import annotations
import time, cv2, logging
from datetime import datetime
from uuid import uuid4
from PySide6.QtCore import QThread, Signal
from camera.camera_manager import CameraManager
from detection.vehicle_detector import VehicleDetector
from detection.tracker import SimpleTracker
from violations.violation_engine import ViolationEngine
from evidence.frame_buffer import FrameBuffer
from evidence.evidence_manager import EvidenceManager
from database.database import Database
from utils.config_loader import load_json, CONFIG_DIR
from alarm.alarm_manager import AlarmManager
class VideoWorker(QThread):
    frame_ready=Signal(object); status=Signal(str); failed=Signal(str); violation=Signal(object)
    def __init__(self,source,zones=None,signal_state='RED'): super().__init__(); self.source=source; self.zones=zones or {}; self.signal_state=signal_state; self.running=True; self.paused=False
    def run(self):
        cam=CameraManager.create(self.source)
        if not cam.open(): self.failed.emit(f'Cannot open camera source: {self.source}'); return
        config=load_json(CONFIG_DIR/'app_config.json',{}); detector=VehicleDetector(config.get('model_path','models/yolo11n.pt'),config.get('confidence_threshold',.4)); tracker=SimpleTracker(); engine=ViolationEngine(config.get('no_parking_grace_seconds',10),config.get('post_alarm_grace_seconds',5)); buffer=FrameBuffer(int(config.get('detection_fps',10)*config.get('evidence_seconds_before',5))); evidence=EvidenceManager(); database=Database(); alarms=AlarmManager(config.get('alarm_enabled',True))
        self.status.emit('Camera connected; monitoring started')
        while self.running:
            if self.paused: self.msleep(50); continue
            ok,frame=cam.read()
            if not ok: self.status.emit('Video ended or camera disconnected'); break
            buffer.add(frame)
            try:
                tracks=tracker.update(detector.detect(frame))
                for track in tracks:
                    x1,y1,x2,y2=map(int,track.box); cv2.rectangle(frame,(x1,y1),(x2,y2),(56,189,248),2); cv2.putText(frame,f'#{track.track_id} {track.label} {track.confidence:.2f}',(x1,max(20,y1-8)),cv2.FONT_HERSHEY_SIMPLEX,.55,(56,189,248),2)
                    for event in engine.evaluate(track,self.zones,self.signal_state):
                        if event.violation_type.endswith('_WARNING'):
                            alarms.trigger_once((track.track_id,event.zone_id)); self.violation.emit({'type':'warning','track_id':track.track_id,'violation_type':event.violation_type}); continue
                        violation_id='V'+uuid4().hex[:10].upper(); metadata={'violation_id':violation_id,'camera_id':'CAM_01','plate_number':None,'violation_type':event.violation_type,'timestamp':datetime.now().isoformat(),'duration_seconds':event.duration,'vehicle_type':track.label,'vehicle_confidence':track.confidence,'plate_confidence':0.0}
                        folder=evidence.create(violation_id,frame,buffer.before(),track.box,metadata,buffer.snapshot())
                        database.add_violation({'id':violation_id,'vehicle_track_id':track.track_id,'plate_number':None,'violation_type':event.violation_type,'camera_id':'CAM_01','timestamp':metadata['timestamp'],'duration':event.duration,'vehicle_type':track.label,'vehicle_confidence':track.confidence,'plate_confidence':0.0,'evidence_path':str(folder),'status':'PENDING_REVIEW','reviewed_by':None,'reviewed_at':None,'note':None})
                        self.violation.emit(metadata)
                self.status.emit(f'Monitoring | Vehicles: {len(tracks)}')
            except Exception as exc: logging.getLogger(__name__).exception('Processing error'); self.status.emit(f'Processing error: {exc}')
            self.frame_ready.emit(frame); self.msleep(1)
        cam.close(); self.status.emit('Camera disconnected')
    def stop(self): self.running=False; self.wait(1500)
