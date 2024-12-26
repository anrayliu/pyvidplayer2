import subprocess
import json
from . import FFMPEG_LOGLVL, Pyvidplayer2Error


class VideoReader:
    def __init__(self, path, probe=False):
        self.frame_count = 0
        self.frame_rate = 0
        self.original_size = (0, 0)
        self.frame = 0

        if probe:
            self._probe(path)

    def _probe(self, path, as_bytes=False):
        # strangely for ffprobe, - is not required to indicate output
        # NOTE: if probing and the path is bad, this will raise an error before the video class does, may cause confusion on what went wrong for users

        try:
            p = subprocess.Popen(f"ffprobe -i {'-' if as_bytes else path} -show_streams -count_packets -select_streams v -loglevel {FFMPEG_LOGLVL} -print_format json", stdin=subprocess.PIPE if as_bytes else None, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")

        info = json.loads(p.communicate(input=path if as_bytes else None)[0])["streams"]
        if len(info) == 0:
            raise Pyvidplayer2Error("No video tracks found")
        info = info[0]

        self.original_size = int(info["width"]), int(info["height"])
        # int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) is not accurate

        try:
            self.frame_count = int(info["nb_frames"])
        except KeyError:
            self.frame_count = int(info["nb_read_packets"])

        self.frame_rate = float(info["avg_frame_rate"].split("/")[0]) / float(info["avg_frame_rate"].split("/")[1])
    
    def isOpened(self):
        pass
    
    def seek(self, index):
        pass

    def read(self):
        pass

    def release(self):
        pass
