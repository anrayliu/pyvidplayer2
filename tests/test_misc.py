import subprocess
import unittest

import pygame
import pyvidplayer2
from pyvidplayer2 import *

from test_video import VIDEO_PATH


class TestVideo(unittest.TestCase):
    # tests get_version_info
    def test_version_metadata(self):
        VER = "0.9.30"

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
