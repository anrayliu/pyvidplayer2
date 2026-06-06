# Object that mimics cv2.VideoCapture to read frames
import subprocess

import numpy as np

from . import get_ffmpeg_loglevel, get_ffmpeg_path
from .error import FFmpegNotFoundError
from .video_reader import VideoReader


class FFMPEGReader(VideoReader):
    def __init__(self, path, probe=True, cuda_device=-1):
        self._process = None

        VideoReader.__init__(self, path, probe)

        self.cuda_device = cuda_device

        self._colour_format = "BGR"

        self._path = path

        try:
            command = self._get_command()

            self._process = subprocess.Popen(command, stdout=subprocess.PIPE)
        except FileNotFoundError as e:
            raise FFmpegNotFoundError(
                "Could not find FFmpeg. "
                "Make sure FFmpeg is installed and accessible via PATH."
            ) from e

    # not guaranteed to be called but since FFmpegReader
    # is more prone to resource leaks than other readers, adding
    # this as an extra precaution
    def __del__(self):
        self.release()

    @staticmethod
    def _end_proc(proc):
        if proc is None:
            return

        if proc.stdout:
            proc.stdout.close()

        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)

    def _get_command(self, index=None):
        return [
            get_ffmpeg_path(),
            # nvidia hardware acceleration
            *(["-hwaccel", "cuda"] if self.cuda_device >= 0 else []),
            # select device
            *(["-init_hw_device",
               f"cuda:{self.cuda_device}"] if self.cuda_device >= 0 else []),
            *(["-ss", self._convert_seconds(index / self.frame_rate)] if index is not None else []),
            "-i", self._path,
            "-loglevel", get_ffmpeg_loglevel(),
            "-map", "0:v:0",
            "-f", "rawvideo",
            "-vf", "format=bgr24",
            "-sn",
            "-an",
            "-"
        ]

    def _convert_seconds(self, seconds):
        seconds = abs(seconds)
        d = str(seconds).split('.')[-1] if '.' in str(seconds) else 0
        h = int(seconds // 3600)
        seconds = seconds % 3600
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{h}:{m}:{s}.{d}"

    def read(self):
        b = self._process.stdout.read(self.original_size[0] * self.original_size[1] * 3)
        if not b:
            has = False
        else:
            has = True
            self.frame += 1

        frame = None
        if has:
            frame = np.frombuffer(b, np.uint8).reshape((self.original_size[1], self.original_size[0], 3))

        return has, frame

    def seek(self, index):
        self.frame = index
        FFMPEGReader._end_proc(self._process)

        # uses input seeking for very fast reading
        self._process = subprocess.Popen(self._get_command(index=index), stdout=subprocess.PIPE)

    def release(self):
        FFMPEGReader._end_proc(self._process)
        VideoReader.release(self)
