from __future__ import annotations
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from gui.zone_editor import ZoneEditor
from gui.video_worker import VideoWorker
from zones.zone_manager import ZoneManager, Zone
from utils.config_loader import load_json, CONFIG_DIR

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Smart Traffic Monitoring System'); self.resize(1280,800); self.zones=ZoneManager(); self.worker=None; self._build(); self._reload_zones()
    def _build(self):
        self.setStyleSheet('QMainWindow{background:#0f172a;color:#e2e8f0} QGroupBox{border:1px solid #334155;margin-top:10px;padding:8px} QPushButton{background:#1e40af;padding:7px;border-radius:4px} QPushButton:hover{background:#2563eb} QComboBox,QLineEdit,QListWidget{background:#1e293b;padding:5px}')
        root=QWidget(); self.setCentralWidget(root); layout=QHBoxLayout(root)
        left=QVBoxLayout(); camera=QGroupBox('CAMERA PANEL'); cl=QVBoxLayout(camera); self.source=QLineEdit(); self.source.setPlaceholderText('MP4 path, webcam index (0), or RTSP URL'); cl.addWidget(self.source)
        for label,fn in [('Open video',self.open_video),('Connect',self.connect),('Disconnect',self.disconnect),('Pause / Resume',self.pause)]: b=QPushButton(label); b.clicked.connect(fn); cl.addWidget(b)
        self.status=QLabel('Idle'); cl.addWidget(self.status); left.addWidget(camera)
        tools=QGroupBox('ZONE CONFIGURATION'); tl=QVBoxLayout(tools); self.tool_group=QButtonGroup(self)
        for label,tool in [('Select','select'),('Draw No Parking','no_parking_zones'),('Draw Free Left','free_left_zones'),('Draw Stop Line','stop_lines'),('Draw Signal ROI','signal_rois')]:
            b=QRadioButton(label); self.tool_group.addButton(b); b.clicked.connect(lambda checked,t=tool:self.editor.set_tool(t)); tl.addWidget(b)
        clear=QPushButton('Clear all zones'); clear.clicked.connect(self.clear_zones); tl.addWidget(clear)
        save=QPushButton('Save zones'); save.clicked.connect(self.save_zones); tl.addWidget(save); left.addWidget(tools); left.addStretch(); layout.addLayout(left,1)
        centre=QVBoxLayout(); self.editor=ZoneEditor(); self.editor.zone_created.connect(self.add_zone); centre.addWidget(self.editor,1); self.signal=QComboBox(); self.signal.addItems(['RED','YELLOW','GREEN']); centre.addWidget(QLabel('Manual signal state')); centre.addWidget(self.signal); layout.addLayout(centre,4)
        self.signal.currentTextChanged.connect(lambda state: setattr(self.worker,'signal_state',state) if self.worker else None)
        right=QVBoxLayout(); alert=QGroupBox('VIOLATION / ALERT PANEL'); al=QVBoxLayout(alert); self.metrics=QLabel('FPS: --\nVehicles: 0\nViolations: 0\nAlarm: Ready'); al.addWidget(self.metrics); self.zone_list=QListWidget(); al.addWidget(self.zone_list); delete=QPushButton('Delete selected zone'); delete.clicked.connect(self.delete_zone); al.addWidget(delete); right.addWidget(alert); right.addStretch(); layout.addLayout(right,1)
    def open_video(self):
        path,_=QFileDialog.getOpenFileName(self,'Open video','','Video (*.mp4 *.avi *.mkv);;All files (*)')
        if path:self.source.setText(path); self.connect()
    def connect(self):
        self.disconnect(); source=self.source.text().strip()
        if not source:self.status.setText('Choose an MP4, webcam index, or RTSP URL'); return
        self.worker=VideoWorker(source,self.zones.data,self.signal.currentText()); self.worker.frame_ready.connect(self.editor.set_frame); self.worker.status.connect(self.status.setText); self.worker.failed.connect(self.status.setText); self.worker.violation.connect(self.on_violation); self.worker.start()
    def disconnect(self):
        if self.worker:self.worker.stop(); self.worker=None
    def pause(self):
        if self.worker:self.worker.paused=not self.worker.paused; self.status.setText('Paused' if self.worker.paused else 'Monitoring')
    def _reload_zones(self):
        self.editor.set_zones(self.zones.data); self.zone_list.clear()
        for kind in ('no_parking_zones','free_left_zones','stop_lines','signal_rois'):
            for z in self.zones.list(kind): self.zone_list.addItem(f'{kind}: {z["id"]}')
    def add_zone(self,kind,payload):
        number=len(self.zones.list(kind))+1; prefix={'no_parking_zones':'NP','free_left_zones':'FL','stop_lines':'SL','signal_rois':'SIG'}[kind]; zid=f'{prefix}_{number:02d}'
        try:self.zones.add(kind,Zone(id=zid,name=zid,points=payload if isinstance(payload,list) else None,**(payload if isinstance(payload,dict) else {}))); self._reload_zones(); self.status.setText(f'Added {zid}')
        except ValueError as exc:self.status.setText(str(exc))
    def delete_zone(self):
        item=self.zone_list.currentItem()
        if item:
            kind,zid=item.text().split(': ',1); self.zones.remove(kind,zid); self._reload_zones()
    def clear_zones(self): self.zones.clear(); self._reload_zones()
    def save_zones(self): self.zones.save(); self.status.setText('Zone configuration saved')
    def on_violation(self,event):
        if event.get('type')=='warning': self.status.setText(f"Warning: {event['violation_type']} on track {event['track_id']}")
        else: self.status.setText(f"Violation {event['violation_id']} saved for review")
    def closeEvent(self,event): self.disconnect(); event.accept()
