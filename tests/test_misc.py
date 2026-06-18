import subprocess
import unittest

import numpy as np
import pygame
import pyvidplayer2
from pyvidplayer2 import (READER_AUTO, READER_DECORD, READER_FFMPEG,
                          READER_IMAGEIO, READER_OPENCV, VERSION,
                          PostProcessing, Video, get_ffmpeg_loglevel,
                          get_ffmpeg_path, get_version_info,
                          set_ffmpeg_loglevel)

from test_video import check_same_frames


class TestMisc(unittest.TestCase):
    # tests get_version_info
    def test_version_metadata(self):
        ver = "0.9.34"

        self.assertEqual(ver, VERSION)
        self.assertEqual(ver, pyvidplayer2.__version__)

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
        from pyvidplayer2 import (READER_AUTO, READER_DECORD, READER_FFMPEG,
                                  READER_IMAGEIO, READER_OPENCV, VERSION,
                                  AudioDeviceError, AudioStreamError,
                                  FFmpegNotFoundError, OpenCVError,
                                  PostProcessing, Pyvidplayer2Error,
                                  SubtitleError, Subtitles, Video, VideoPlayer,
                                  VideoPyglet, VideoPyQT, VideoPySide,
                                  VideoRaylib, VideoStreamError, VideoTkinter,
                                  VideoWx, Webcam, WebcamNotFoundError,
                                  YTDLPError, get_ffmpeg_loglevel,
                                  get_ffmpeg_path, get_ffprobe_path,
                                  get_version_info, set_ffmpeg_loglevel,
                                  set_ffmpeg_path, set_ffprobe_path)
        from pyvidplayer2._version import __version__
        import pyvidplayer2
        self.assertEqual(len(pyvidplayer2.__all__), 33)

    # tests each post processing function
    def test_post_processing(self):
        # must be done with clip.mp4 because trailer1.mp4 fails letterbox due to it already having one
        # and trailer2.mp4 fails noise due to the black opening frames

        v1 = Video("resources/clip.mp4")
        original_frame = next(v1)
        v2 = Video("resources/clip.mp4")
        new_frame = next(v2)
        self.assertTrue(check_same_frames(original_frame, new_frame))

        for func in (
            lambda d: np.fliplr(d),
            PostProcessing.blur,
            PostProcessing.sharpen,
            PostProcessing.greyscale,
            PostProcessing.noise,
            PostProcessing.letterbox,
            PostProcessing.cel_shading,
            PostProcessing.flipup,
            PostProcessing.fliplr,
            PostProcessing.rotate90,
            PostProcessing.rotate270,
            PostProcessing.vhs,
            PostProcessing.emboss
        ):
            v2.set_post_func(func)
            self.assertFalse(check_same_frames(next(v1), next(v2)))

        v1.close()
        v2.close()
