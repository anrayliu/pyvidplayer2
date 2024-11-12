'''
Object that mimics cv2.VideoCapture to read frames
'''

import numpy as np
import subprocess
import json
from . import FFMPEG_LOGLVL


class FFMPEGReader:
    def __init__(self, path):
        self._path = path
        self._opened = False

        self.frame = 0
        self.frame_count = 0
        self.frame_rate = 0
        self.original_size = (0, 0)

        if self._probe():
            self._process = subprocess.Popen(f"ffmpeg -i {self._path} -loglevel {FFMPEG_LOGLVL} -f rawvideo -vf format=bgr24 -sn -an -", stdout=subprocess.PIPE)
            self._opened = True

    def _probe(self):
        # strangely for ffprobe, - is not required to indicate output
        
        try:
            p = subprocess.Popen(f"ffprobe -i {self._path} -show_streams -count_packets -select_streams v -loglevel {FFMPEG_LOGLVL} -print_format json", stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")
        
        try:
            info = json.loads(p.communicate()[0])["streams"][0]
        except KeyError:
            return False

        self.original_size = int(info["width"]), int(info["height"])
        try:
            self.frame_count = int(info["nb_read_packets"])
        except KeyError:
            self.frame_count = int(info["nb_frames"])
        self.frame_rate = float(info["avg_frame_rate"].split("/")[0]) / float(info["avg_frame_rate"].split("/")[1])

        return True

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
        return self._opened