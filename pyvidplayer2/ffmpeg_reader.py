import subprocess 
import json
import numpy as np
from io import BytesIO
from threading import Thread
from functools import partial


class FFMPEGReader:
    def __init__(self, bytes_):
        self.bytes = bytes_

        self.frame = 0
        self.frame_count = 0
        self.frame_rate = 0
        self.original_size = (0, 0)

        self._probe()

        self.stream = BytesIO(self.bytes)
        self.process = subprocess.Popen(f"ffmpeg -i - -loglevel quiet -f rawvideo -vf format=bgr24 -sn -an -", stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        self.thread = Thread(target=self._threaded_write)
        self.thread.start()

    def _threaded_write(self):
        for chunk in iter(partial(self.stream.read, 1024), b''):
            try:
                self.process.stdin.write(chunk)
            except BrokenPipeError:
                return
            
        self.process.stdin.close()
    
    def _probe(self):
        # strangely for ffprobe, - is not required to indicate output
        
        try:
            p = subprocess.Popen(f"ffprobe -i - -show_streams -count_frames -select_streams v -loglevel quiet -print_format json", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")
        
        info = json.loads(p.communicate(input=self.bytes)[0])["streams"][0]

        self.original_size = int(info["width"]), int(info["height"])
        self.frame_count = int(info["nb_read_frames"])
        self.frame_rate = float(info["r_frame_rate"].split("/")[0]) / float(info["r_frame_rate"].split("/")[1])

    def read(self):
        b = self.process.stdout.read(self.original_size[0] * self.original_size[1] * 3)
        if not b:
            has = False 
        else:
            has = True
            self.frame += 1

        return has, np.frombuffer(b, np.uint8).reshape((self.original_size[1], self.original_size[0], 3)) if has else None

    def seek(self, index):
        self.stream.seek(int(index * self.original_size[0] * self.original_size[1] * 3))

    def release(self):
        self.process.terminate()
        self.thread.join()
        self.bytes = b''

    def isOpened(self):
        return True