import subprocess
import json
from . import FFMPEG_LOGLVL
from .error import *


class VideoReader:
    def __init__(self, path, probe=False):
        self.frame_count = 0
        self.frame_rate = 0
        self.original_size = (0, 0)
        self.duration = 0
        self.frame = 0
        self._colour_format = ""

        self.released = False

        if probe:
            self._probe(path)

    # as it turns out, obtaining video data such as frame count and dimensions is actually very inconsistent between
    # different videos and encoders
    def _probe(self, path, as_bytes=False):
        # strangely for ffprobe, - is not required to indicate output

        try:
            # this method counts the number of packets as a substitute for frames, which is much too slow
            #p = subprocess.Popen(f"ffprobe -i {'-' if as_bytes else path} -show_streams -select_streams v -loglevel {FFMPEG_LOGLVL} -print_format json", stdin=subprocess.PIPE if as_bytes else None, stdout=subprocess.PIPE)
            p = subprocess.Popen(f"ffprobe -i {'-' if as_bytes else path} -show_streams -count_packets -select_streams v:0 -loglevel {FFMPEG_LOGLVL} -print_format json", stdin=subprocess.PIPE if as_bytes else None, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FFmpegNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")

        info = json.loads(p.communicate(input=path if as_bytes else None)[0])

        if len(info) == 0:
            raise VideoStreamError("Could not determine video.")
        info = info["streams"]
        if len(info) == 0:
            raise VideoStreamError("No video tracks found.")
        info = info[0]

        self.original_size = int(info["width"]), int(info["height"])

        if self.original_size == (0, 0):
            raise VideoStreamError("FFmpeg failed to read video.")

        self.frame_rate = float(info["r_frame_rate"].split("/")[0]) / float(info["r_frame_rate"].split("/")[1])

        # this detects duration instead

        '''try:
            p = subprocess.Popen(f"ffprobe -i {'-' if as_bytes else path} -show_format -loglevel {FFMPEG_LOGLVL} -print_format json",
                stdin=subprocess.PIPE if as_bytes else None, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError(
                "Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")

        info = json.loads(p.communicate(input=path if as_bytes else None)[0])["format"]
        self.duration = float(info["duration"])
        self.frame_count = int(self.duration * self.frame_rate)'''

        # use header information if available, which should be more accurate than counting packets
        try:
            self.frame_count = int(info["nb_frames"])
        except KeyError:
            self.frame_count = int(info["nb_read_packets"])

        try:
            self.duration = float(info["duration"])
        except KeyError:
            self.duration = self.frame_count / self.frame_rate

    def isOpened(self):
        return True
    
    def seek(self, index):
        pass

    def read(self):
        pass

    def release(self):
        self.released = True
