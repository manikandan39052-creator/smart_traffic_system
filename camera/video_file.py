import cv2
from camera.base_camera import CameraSource
class VideoFileSource(CameraSource):
    def __init__(self,path): self.path=path; self.capture=None
    def open(self): self.capture=cv2.VideoCapture(self.path); return self.capture.isOpened()
    def read(self): return self.capture.read() if self.capture else (False,None)
    def close(self):
        if self.capture:self.capture.release()
