import cv2 


class CVReader:
    def __init__(self, path):
        self.vidcap = cv2.VideoCapture(path)

        self.frame_count = int(self.vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = self.vidcap.get(cv2.CAP_PROP_FPS)
        self.original_size = (int(self.vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    
    @property
    def frame(self):
        return int(self.vidcap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def isOpened(self):
        return self.vidcap.isOpened()
    
    def seek(self, index):
        self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, index)

    def read(self):
        return self.vidcap.read()

    def release(self):
        self.vidcap.release()