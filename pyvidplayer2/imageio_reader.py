import imageio.v3 as iio
import subprocess
import json 
from . import FFMPEG_LOGLVL


class IIOReader:
    '''
    This video reader uses imageio. All video readers must follow the following structure:

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

    def __init__(self, path):
        self.frame = 0
        self.frame_count = 0
        self.frame_rate = 0
        self.original_size = (0, 0)

        self._path = path
        self._opened = False
        self._gen = None
        self._as_bytes = isinstance(path, bytes)
        
        if self._probe():
            self.seek(0)
            self._opened = True

    def _probe(self):
        # strangely for ffprobe, - is not required to indicate output
        
        try:
            p = subprocess.Popen(f"ffprobe -i {'-' if self._as_bytes else self._path} -show_streams -count_packets -select_streams v -loglevel {FFMPEG_LOGLVL} -print_format json", stdin=subprocess.PIPE if self._as_bytes else None, stdout=subprocess.PIPE)
        except FileNotFoundError:
            raise FileNotFoundError("Could not find FFPROBE (should be bundled with FFMPEG). Make sure FFPROBE is installed and accessible via PATH.")
        
        try:
            info = json.loads(p.communicate(input=self._path if self._as_bytes else None)[0])["streams"][0]
        except KeyError:
            return False

        self.original_size = int(info["width"]), int(info["height"])
        self.frame_count = int(info["nb_read_packets"])
        self.frame_rate = float(info["avg_frame_rate"].split("/")[0]) / float(info["avg_frame_rate"].split("/")[1])

        return True

    def isOpened(self):
        return self._opened
    
    def seek(self, index):
        del self._gen 

        # thread_type="FRAME" sets multithreading

        new_gen = iio.imiter(self._path, plugin="pyav", thread_type="FRAME")
        try:
            for i in range(int(index)):
                next(new_gen)
        except StopIteration:
            index = self.frame_count - 1

        self.frame = index
        self._gen = new_gen

    def read(self):
        has = True
        try:
            frame = next(self._gen)
        except StopIteration:
            has = False
            frame = None
        else:
            self.frame += 1

        # unfortunately for this particular reader it is converting from RGB to BGR,
        # then it will be converted back from BGR to RGB for rendering
        return has, frame[...,::-1] if has else None

    def release(self):
        self._path = b''
