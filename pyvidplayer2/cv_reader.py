import cv2 
import subprocess
import json
from . import FFMPEG_LOGLVL
from .error import Pyvidplayer2Error


class CVReader:
    '''
    This video reader uses opencv. All video readers must follow the following structure:

    Parameters:
        None
    
    Attributes:
        frame_count: int
        frame_rate: float
        original_size: (int, int)
        frame: int

    Methods:
        isOpened() -> bool
        seek(i: int) -> None
        read() -> (bool, np.ndarray)
        release() -> None
    '''

    def __init__(self, path, probe=False):
        self._vidcap = cv2.VideoCapture(path)
        self._path = path

        self.frame_count = int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = self._vidcap.get(cv2.CAP_PROP_FPS)
        self.original_size = (int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # webm videos have negative frame counts for some reason
        if probe or self.frame_count < 0:
            self._probe()

    # provides more accurate information

    def _probe(self):
        # strangely for ffprobe, - is not required to indicate output
        # NOTE: if probing and the path is bad, this will raise an error before the video class does, may cause confusion on what went wrong for users
        
        try:
            p = subprocess.Popen(f"ffprobe -i {self._path} -show_streams -count_packets -select_streams v -loglevel {FFMPEG_LOGLVL} -print_format json", stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")

        info = json.loads(p.communicate()[0])["streams"]
        if len(info) == 0:
            raise Pyvidplayer2Error("No video tracks found.")
        else:
            info = info[0]
        
        self.original_size = int(info["width"]), int(info["height"])
        # int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) is not accurate
        try:
            self.frame_count = int(info["nb_read_packets"])
        except KeyError:
            self.frame_count = int(info["nb_frames"])
        self.frame_rate = float(info["avg_frame_rate"].split("/")[0]) / float(info["avg_frame_rate"].split("/")[1])

    @property
    def frame(self):
        return int(self._vidcap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def isOpened(self):
        return self._vidcap.isOpened()
    
    def seek(self, index):
        self._vidcap.set(cv2.CAP_PROP_POS_FRAMES, index)

    def read(self):
        return self._vidcap.read()

    def release(self):
        self._vidcap.release()
