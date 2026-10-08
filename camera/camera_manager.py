from camera.video_file import VideoFileSource
from camera.webcam import WebcamSource
from camera.rtsp_camera import RTSPSource
class CameraManager:
    @staticmethod
    def create(source):
        if str(source).isdigit(): return WebcamSource(int(source))
        if str(source).lower().startswith('rtsp://'): return RTSPSource(source)
        return VideoFileSource(source)
