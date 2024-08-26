import cv2 


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

    def __init__(self, path):
        self._vidcap = cv2.VideoCapture(path)

        self.frame_count = int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = self._vidcap.get(cv2.CAP_PROP_FPS)
        self.original_size = (int(self._vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    
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