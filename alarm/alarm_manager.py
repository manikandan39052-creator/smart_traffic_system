from __future__ import annotations
from PySide6.QtWidgets import QApplication
class AlarmManager:
    def __init__(self, enabled=True): self.enabled=enabled; self.fired=set()
    def trigger_once(self,key):
        if self.enabled and key not in self.fired: self.fired.add(key); QApplication.beep(); return True
        return False
