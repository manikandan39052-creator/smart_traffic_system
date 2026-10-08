"""Mouse-driven zone editor rendered over the latest video frame."""
from __future__ import annotations
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap, QPolygon
from PySide6.QtWidgets import QLabel
import cv2, numpy as np

COLORS={"no_parking_zones":QColor('#ef5350'),"free_left_zones":QColor('#ffca28'),"stop_lines":QColor('#42a5f5'),"signal_rois":QColor('#ab47bc')}
class ZoneEditor(QLabel):
    zone_created=Signal(str, object)
    def __init__(self):
        super().__init__('Connect a camera or open a video'); self.setAlignment(Qt.AlignCenter); self.setMinimumSize(760,500); self.setStyleSheet('background:#111827; border:1px solid #334155; color:#94a3b8;')
        self.frame=None; self.zones={k:[] for k in COLORS}; self.tool="select"; self.points=[]; self.mouse=None
    def set_tool(self,tool): self.tool=tool; self.points=[]; self.update()
    def set_zones(self,zones): self.zones={k:list(zones.get(k,[])) for k in COLORS}; self.update()
    def set_frame(self,frame):
        self.frame=frame.copy(); rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB); h,w,_=rgb.shape; self.setPixmap(QPixmap.fromImage(QImage(rgb.data,w,h,w*3,QImage.Format_RGB888).copy()).scaled(self.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation)); self.update()
    def _map(self,p):
        if self.frame is None or not self.pixmap(): return None
        pm=self.pixmap(); ox=(self.width()-pm.width())/2; oy=(self.height()-pm.height())/2
        x=(p.x()-ox)*self.frame.shape[1]/pm.width(); y=(p.y()-oy)*self.frame.shape[0]/pm.height()
        return [max(0,min(int(x),self.frame.shape[1]-1)),max(0,min(int(y),self.frame.shape[0]-1))]
    def _canvas(self,p):
        if self.frame is None or not self.pixmap(): return QPoint()
        pm=self.pixmap(); return QPoint(int(p[0]*pm.width()/self.frame.shape[1]+(self.width()-pm.width())/2),int(p[1]*pm.height()/self.frame.shape[0]+(self.height()-pm.height())/2))
    def paintEvent(self,event):
        super().paintEvent(event); painter=QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        for kind,items in self.zones.items():
            painter.setPen(QPen(COLORS[kind],3));
            for z in items:
                if kind=="signal_rois":
                    p=self._canvas([z['x'],z['y']]); p2=self._canvas([z['x']+z['width'],z['y']+z['height']]); painter.drawRect(p.x(),p.y(),p2.x()-p.x(),p2.y()-p.y())
                else:
                    pts=[self._canvas(v) for v in z['points']]
                    if len(pts)>1: painter.drawPolyline(QPolygon(pts)) if kind=="stop_lines" else painter.drawPolygon(QPolygon(pts))
        if self.points:
            kind=self.tool; painter.setPen(QPen(COLORS.get(kind,QColor('white')),2,Qt.DashLine)); pts=[self._canvas(p) for p in self.points]
            if self.mouse: pts.append(self._canvas(self.mouse))
            if len(pts)>1: painter.drawPolyline(QPolygon(pts))
            for p in pts: painter.drawEllipse(p,4,4)
    def mousePressEvent(self,event):
        p=self._map(event.position().toPoint())
        if p is None:return
        if event.button()==Qt.RightButton: self.points=[]; self.update(); return
        if self.tool=="select":return
        self.points.append(p)
        if self.tool=="stop_lines" and len(self.points)==2:self.finish()
        if self.tool=="signal_rois" and len(self.points)==2:self.finish()
        self.update()
    def mouseMoveEvent(self,event): self.mouse=self._map(event.position().toPoint()); self.update()
    def mouseDoubleClickEvent(self,event):
        if self.tool in ("no_parking_zones","free_left_zones"): self.finish()
    def finish(self):
        if self.tool in ("no_parking_zones","free_left_zones") and len(self.points)>=3: self.zone_created.emit(self.tool,self.points)
        elif self.tool=="stop_lines" and len(self.points)==2:self.zone_created.emit(self.tool,self.points)
        elif self.tool=="signal_rois" and len(self.points)==2:
            a,b=self.points; self.zone_created.emit(self.tool,{"x":min(a[0],b[0]),"y":min(a[1],b[1]),"width":abs(a[0]-b[0]),"height":abs(a[1]-b[1])})
        self.points=[]; self.update()
