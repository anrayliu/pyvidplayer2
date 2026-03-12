import subprocess
import unittest

import pyvidplayer2
from pyvidplayer2 import *

# trigger code in test_video in case this file is executed before
import test_video


class TestMisc(unittest.TestCase):
    # tests get_version_info
    def test_version_metadata(self):
        VER = "0.9.31"

        self.assertEqual(VER, VERSION)
        self.assertEqual(VER, pyvidplayer2.__version__)

        info = get_version_info()

        try:
            ffmpeg_ver = subprocess.run([get_ffmpeg_path(), "-version"], capture_output=True, universal_newlines=True).stdout.split(" ")[2]
        except FileNotFoundError:
            ffmpeg_ver = "not installed"

        self.assertEqual(info["pyvidplayer2"], VERSION)
        self.assertEqual(info["ffmpeg"], ffmpeg_ver)
        self.assertEqual(info["pygame"], pygame.version.ver)

    # tests that enums are the correct values
    # could cause problems if they somehow overlap with each other
    def test_enums(self):
        self.assertEqual(READER_AUTO, 0)
        self.assertEqual(READER_FFMPEG, 1)
        self.assertEqual(READER_OPENCV, 2)
        self.assertEqual(READER_IMAGEIO, 3)
        self.assertEqual(READER_DECORD, 4)

    # tests that ffmpeg logs are hidden in case they were turned on and forgotten
    def test_loglevels(self):
        self.assertEqual(get_ffmpeg_loglevel(), "quiet")

        for level in (
            "quiet",
            "panic",
            "fatal",
            "error",
            "warning",
            "info",
            "verbose",
            "debug",
            "trace"
        ):
            set_ffmpeg_loglevel(level)
            self.assertEqual(get_ffmpeg_loglevel(), level)

        set_ffmpeg_loglevel("badlevel")
        self.assertEqual(get_ffmpeg_loglevel(), "trace")

        # reset for other unit tests
        set_ffmpeg_loglevel("quiet")

    # tests API validity
    # noinspection PyUnresolvedReferences
    def test_library_interface(self):
        from pyvidplayer2 import Video
        from pyvidplayer2 import VideoTkinter
        from pyvidplayer2 import VideoPySide
        from pyvidplayer2 import VideoPyQT
        from pyvidplayer2 import VideoPyglet
        from pyvidplayer2 import VideoRaylib
        from pyvidplayer2 import VideoWx
        from pyvidplayer2 import VideoPlayer
        from pyvidplayer2 import Webcam
        from pyvidplayer2 import Subtitles

        from pyvidplayer2 import get_version_info
        from pyvidplayer2 import get_ffmpeg_path
        from pyvidplayer2 import set_ffmpeg_path
        from pyvidplayer2 import get_ffprobe_path
        from pyvidplayer2 import set_ffprobe_path
        from pyvidplayer2 import get_ffmpeg_loglevel
        from pyvidplayer2 import set_ffmpeg_loglevel

        from pyvidplayer2 import READER_FFMPEG
        from pyvidplayer2 import READER_DECORD
        from pyvidplayer2 import READER_OPENCV
        from pyvidplayer2 import READER_IMAGEIO
        from pyvidplayer2 import READER_AUTO

        from pyvidplayer2 import Pyvidplayer2Error
        from pyvidplayer2 import AudioDeviceError
        from pyvidplayer2 import AudioStreamError
        from pyvidplayer2 import SubtitleError
        from pyvidplayer2 import VideoStreamError
        from pyvidplayer2 import FFmpegNotFoundError
        from pyvidplayer2 import OpenCVError
        from pyvidplayer2 import YTDLPError
        from pyvidplayer2 import WebcamNotFoundError

        from pyvidplayer2 import PostProcessing
        from pyvidplayer2 import VERSION
        from pyvidplayer2._version import __version__
