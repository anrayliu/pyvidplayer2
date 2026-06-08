from io import BytesIO

import decord

from .error import VideoStreamError
from .video_reader import VideoReader


class DecordReader(VideoReader):
    def __init__(self, path):
        VideoReader.__init__(self, path, False)

        self._colour_format = "RGB"

        self._path = path
        self._as_bytes = isinstance(path, bytes)

        try:
            self._vid_reader = decord.VideoReader(BytesIO(path) if self._as_bytes else path)
        except RuntimeError as e:
            raise VideoStreamError("Could not determine video.") from e

        VideoReader._probe(self, path, self._as_bytes)

    def seek(self, index):
        try:
            self._vid_reader.seek_accurate(index)
        except AssertionError:
            pass  # index out of bounds
        self.frame = index  # don't put this into an "else" block

    def read(self):
        frame = None
        has_frame = False
        try:
            frame = self._vid_reader.next().asnumpy()
        except StopIteration:
            pass
        else:
            has_frame = True
            self.frame += 1

        return has_frame, frame

    def release(self):
        self._path = b''
        VideoReader.release(self)
