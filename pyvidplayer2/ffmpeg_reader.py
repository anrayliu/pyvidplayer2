'''
Object that mimics cv2.VideoCapture to read frames
'''

import numpy as np
import subprocess
from . import FFMPEG_LOGLVL
from .video_reader import VideoReader
from .error import *


class FFMPEGReader(VideoReader):
    def __init__(self, path, probe=True):
        VideoReader.__init__(self, path, probe)

        self._colour_format = "BGR"

        try:
            self._process = subprocess.Popen(f"ffmpeg -i {path} -loglevel {FFMPEG_LOGLVL} -map 0:v:0 -f rawvideo -vf format=bgr24 -sn -an -", stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FFmpegNotFoundError("Could not find FFmpeg. Make sure FFmpeg is installed and accessible via PATH.")

        self._path = path

    def _convert_seconds(self, seconds):
        seconds = abs(seconds)
        d = str(seconds).split('.')[-1] if '.' in str(seconds) else 0
        h = int(seconds // 3600)
        seconds = seconds % 3600
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{h}:{m}:{s}.{d}"

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
        self._process.kill()
        # uses input seeking for very fast reading
        self._process = subprocess.Popen(f"ffmpeg -ss {self._convert_seconds(index / self.frame_rate)} -i {self._path} -loglevel {FFMPEG_LOGLVL} -map 0:v:0 -f rawvideo -vf format=bgr24 -sn -an -", stdout=subprocess.PIPE)
        
    def release(self):
        self._process.kill()
        VideoReader.release(self)
