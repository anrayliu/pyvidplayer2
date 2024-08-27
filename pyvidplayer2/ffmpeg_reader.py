'''
Video frame reader using only ffmpeg and ffprobe
Obsolete now, replaced with IIOReader
'''

import subprocess 
import json
import numpy as np
from io import BytesIO
from threading import Thread
from functools import partial
from . import FFMPEG_LOGLVL


class FFMPEGReader:
    def __init__(self, bytes_):
        self._bytes = bytes_

        self.frame = 0
        self.frame_count = 0
        self.frame_rate = 0
        self.original_size = (0, 0)

        self._probe()

        self._stream = BytesIO(self._bytes)
        self._process = subprocess.Popen(f"ffmpeg -i - -loglevel {FFMPEG_LOGLVL} -f rawvideo -vf format=bgr24 -sn -an -", stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        self._thread = Thread(target=self._threaded_write)
        self._thread.start()

    def _threaded_write(self):
        for chunk in iter(partial(self._stream.read, 1024), b''):
            try:
                self._process.stdin.write(chunk)
            except BrokenPipeError:
                return
            
        self._process.stdin.close()
    
    def _probe(self):
        # strangely for ffprobe, - is not required to indicate output
        
        try:
            p = subprocess.Popen(f"ffprobe -i - -show_streams -count_frames -select_streams v -loglevel {FFMPEG_LOGLVL} -print_format json", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")
        
        info = json.loads(p.communicate(input=self._bytes)[0])["streams"][0]

        self.original_size = int(info["width"]), int(info["height"])
        self.frame_count = int(info["nb_read_frames"])
        self.frame_rate = float(info["avg_frame_rate"].split("/")[0]) / float(info["avg_frame_rate"].split("/")[1])

    def read(self):
        b = self._process.stdout.read(self.original_size[0] * self.original_size[1] * 3)
        if not b:
            has = False 
        else:
            has = True
            self.frame += 1

        return has, np.frombuffer(b, np.uint8).reshape((self.original_size[1], self.original_size[0], 3)) if has else None

    def seek(self, index):
        self._stream.seek(int(index * self.original_size[0] * self.original_size[1] * 3))

    def release(self):
        self._process.terminate()
        self._thread.join()
        self._bytes = b''

    def isOpened(self):
        return True