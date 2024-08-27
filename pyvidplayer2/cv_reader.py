import cv2 
import subprocess
import json
from . import FFMPEG_LOGLVL


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

    def __init__(self, path, precise=False):
        self._vidcap = cv2.VideoCapture(path)
        self._path = path

        self.frame_count = int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = self._vidcap.get(cv2.CAP_PROP_FPS)
        self.original_size = (int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        if precise:
            self._probe()

    def _probe(self):
        # strangely for ffprobe, - is not required to indicate output
        
        try:
            p = subprocess.Popen(f"ffprobe -i {self._path} -show_streams -show_entries stream_tags=rotate -count_frames -select_streams v -loglevel {FFMPEG_LOGLVL} -print_format json", stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")
        
        info = json.loads(p.communicate()[0])["streams"][0]

        self.original_size = int(info["width"]), int(info["height"])

        try:
            # adjusts for correct dimensions, but does not actually account for video rotation yet
            for i in range(int(info["side_data_list"][0]["rotation"]) % 90 + 1):
                self.original_size = self.original_size[1], self.original_size[0]
        except KeyError:
            pass    # video does not contain info about rotation
        
        # int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) is not accurate
        self.frame_count = int(info["nb_read_frames"])
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