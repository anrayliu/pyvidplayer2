# test resources: https://github.com/anrayliu/pyvidplayer2-test-resources
# use pip install pyvidplayer2[all] to install all dependencies


import unittest
import time
import sys
from threading import Thread
from pyvidplayer2 import *
from test_video import VIDEO_PATH
from test_youtube import YOUTUBE_PATH

# macos and linux os' do not like preview tests, so I've isolated them here
# can still be buggy on windows, so this test file may be omitted


class TestPreviews(unittest.TestCase):
    # tests that looping is seamless
    # also tests that video does indeed loop by timing out otherwise
    def test_seamless_loop(self):
        v = Video("resources/loop.mp4")
        vp = VideoPlayer(v, (0, 0, *v.original_size), loop=True)

        self.assertTrue(v._buffer_first_chunk)

        thread = Thread(target=lambda: vp.preview())
        thread.start()

        t = 0
        track = False
        buffers = []
        timeout = time.time()
        while True:
            if time.time() - timeout > 30:
                raise TimeoutError("Test timed out.")
            if not v.active and not track:
                t = time.time()
                track = True
            elif v.active and track:
                track = False
                buffers.append(time.time() - t)
                if len(buffers) == 10:
                    self.assertTrue(v.frame_delay > sum(buffers) / 10.0)
                    break

        # gracefully shut down thread which would otherwise loop forever
        vp.loop = False
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        thread.join()

        vp.close()

    # tests for a bug where previews would never end if video was looping
    # for some reason, this fails if ran with the rest, but passes when ran individually
    @unittest.skip
    def test_looping_preview(self):
        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, *v.original_size), loop=True)

        thread = Thread(target=lambda: vp.preview())
        thread.start()

        time.sleep(0.5)
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        time.sleep(0.5)

        if v.active:
            # gracefully shut down thread which would otherwise loop forever
            vp.loop = False
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            thread.join()

            # make v active again to raise an assertion error
            v.active = True

        self.assertFalse(v.active)

        vp.close()
        thread.join()

    # tests that previews behave correctly
    @unittest.skip
    def test_preview(self):
        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, 1280, 720))
        v.seek(v.duration)
        thread = Thread(target=lambda: vp.preview())
        thread.start()
        time.sleep(1)
        self.assertFalse(thread.is_alive())
        self.assertTrue(vp.closed)
        thread.join()

    # tests that previews start from where the video position is, and that they close the video afterwards
    def test_previews(self):
        for lib in (Video, VideoTkinter, VideoPyglet, VideoRaylib, VideoPyQT, VideoPySide, VideoWx):
            v = lib(VIDEO_PATH)
            v.seek(v.duration)
            v.preview()
            self.assertTrue(v.closed)

    # tests pyav dependency message
    def test_imageio_needs_pyav(self):
        # mocks away av
        dict_ = {key: None for key in sys.modules.keys() if key.startswith("av.")}
        dict_.update({"av": None})
        with unittest.mock.patch.dict("sys.modules", dict_):
            with self.assertRaises(ImportError) as context:
                Video("resources/clip.mp4", reader=READER_IMAGEIO).preview()


    # tests for a bug where the last frame would hang in situations like this
    def test_frame_bug(self):
        v = Video(VIDEO_PATH, speed=5)
        v.seek(65.19320347222221, False)
        thread = Thread(target=lambda: v.preview())
        thread.start()
        time.sleep(1)
        self.assertFalse(thread.is_alive())
        thread.join()

    # tests for videos with special characters in their title (e.g spaces, symbols, etc)
    def test_special_filename(self):
        v = Video("resources/specia1 video$% -.mp4", speed=5)
        thread = Thread(target=lambda: v.preview())
        thread.start()
        time.sleep(2)
        self.assertFalse(thread.is_alive())
        thread.join()

    # test that gifs can be played
    def test_gif(self):
        v = Video("resources/myGif.gif")
        thread = Thread(target=lambda: v.preview())
        thread.start()
        time.sleep(1.5)
        self.assertFalse(thread.is_alive())
        thread.join()

    # tests that video players work with youtube videos
    def test_youtube_player(self):
        v = Video(YOUTUBE_PATH, youtube=True)
        vp = VideoPlayer(v, (0, 0, *v.original_size))
        v.seek(v.duration)
        thread = Thread(target=lambda: vp.preview())
        thread.start()
        time.sleep(1)
        self.assertFalse(thread.is_alive())
        self.assertTrue(vp.closed)
        thread.join()
