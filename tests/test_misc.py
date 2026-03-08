import subprocess
import unittest

import pygame
import pyvidplayer2


class TestVideo(unittest.TestCase):
    # tests get_version_info
    def test_version_metadata(self):
        VER = "0.9.30"

        self.assertEqual(VER, pyvidplayer2.VERSION)
        self.assertEqual(VER, pyvidplayer2.__version__)

        info = pyvidplayer2.get_version_info()

        try:
            ffmpeg_ver = subprocess.run(["ffmpeg", "-version"], capture_output=True, universal_newlines=True).stdout.split(" ")[2]
        except FileNotFoundError:
            ffmpeg_ver = "not installed"

        self.assertEqual(info["pyvidplayer2"], pyvidplayer2.VERSION)
        self.assertEqual(info["ffmpeg"], ffmpeg_ver)
        self.assertEqual(info["pygame"], pygame.version.ver)

    # tests that enums are the correct values
    # could cause problems if they somehow overlap with each other
    def test_enums(self):
        self.assertEqual(pyvidplayer2.READER_AUTO, 0)
        self.assertEqual(pyvidplayer2.READER_FFMPEG, 1)
        self.assertEqual(pyvidplayer2.READER_OPENCV, 2)
        self.assertEqual(pyvidplayer2.READER_IMAGEIO, 3)
        self.assertEqual(pyvidplayer2.READER_DECORD, 4)

    # tests that ffmpeg logs are hidden in case they were turned on and forgotten
    def test_loglevels(self):
        self.assertEqual(pyvidplayer2.FFMPEG_LOGLVL, "quiet")
