import imageio.v3 as iio
from .video_reader import VideoReader


class IIOReader(VideoReader):
    def __init__(self, path):
        VideoReader.__init__(self, path, False)

        self._colour_format = "RGB"

        self._path = path
        self._gen = None
        self._as_bytes = isinstance(path, bytes)

        VideoReader._probe(self, path, self._as_bytes)
        self.seek(0)

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
        has = False
        frame = None
        try:
            frame = next(self._gen)
        except StopIteration:
            pass
        except AttributeError:  # for pyav v14 and imageio bug
            pass
        else:
            has = True
            self.frame += 1

        return has, frame if has else None

    def release(self):
        self._path = b''
        self._gen = None
        VideoReader.release(self)
