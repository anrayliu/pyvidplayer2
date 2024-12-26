'''
Object that mimics cv2.VideoCapture to read frames
'''

import numpy as np
import subprocess
from . import FFMPEG_LOGLVL
from .video_reader import VideoReader


class FFMPEGReader(VideoReader):
    def __init__(self, path):
        VideoReader.__init__(self, path, True)

        self._process = subprocess.Popen(f"ffmpeg -i {path} -loglevel {FFMPEG_LOGLVL} -f rawvideo -vf format=bgr24 -sn -an -", stdout=subprocess.PIPE)
        self._path = path

    def _convert_seconds(self, seconds):
        h = int(seconds // 3600)
        seconds = seconds % 3600
        m = int(seconds // 60)
        s = int(seconds % 60)
        d = round(seconds % 1, 1)
        return f"{h}:{m}:{s}.{int(d * 10)}"

    def read(self):
        b = self._process.stdout.read(self.original_size[0] * self.original_size[1] * 3)
        if not b:
            has = False
        else:
            has = True
            self.frame += 1

        return has, np.frombuffer(b, np.uint8).reshape((self.original_size[1], self.original_size[0], 3)) if has else None

    def seek(self, index):
        self.frame = index
        self._process.terminate()
        # uses input seeking for very fast reading
        self._process = subprocess.Popen(f"ffmpeg -ss {self._convert_seconds(index / self.frame_rate)} -i {self._path} -loglevel {FFMPEG_LOGLVL} -f rawvideo -vf format=bgr24 -sn -an -", stdout=subprocess.PIPE)
        
    def release(self):
        self._process.terminate()


    def isOpened(self):
        return True
