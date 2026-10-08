from camera.video_file import VideoFileSource
class WebcamSource(VideoFileSource):
    def __init__(self,index=0): super().__init__(int(index))
