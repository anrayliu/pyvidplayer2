from .error import *
import cv2
from .video_reader import VideoReader


class CVReader(VideoReader):
    def __init__(self, path, probe=False):
        VideoReader.__init__(self, path, probe)

        self._colour_format = "BGR"

        self._vidcap = cv2.VideoCapture(path)
        if not self.isOpened():
            return

        if not probe:
            self.frame_count = int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_rate = self._vidcap.get(cv2.CAP_PROP_FPS)
            self.original_size = (int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self.duration = self.frame_count / self.frame_rate

            # webm videos have negative frame counts
            if self.frame_count < 0:
                VideoReader._probe(self, path, False)

    def isOpened(self):
        return self._vidcap.isOpened()
    
    def seek(self, index):
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, index)
        self.frame = int(self._vidcap.get(cv2.CAP_PROP_POS_FRAMES))
        if self.frame < 0:
            raise OpenCVError("Failed to seek.")

    def read(self):
        has, frame = self._vidcap.read()
        if has:
            self.frame += 1
        return has, frame

    def release(self):
        self._vidcap.release()
        VideoReader.release(self)
