# test resources: https://github.com/anrayliu/pyvidplayer2-test-resources


import sys
import time
import unittest
from threading import Thread

import pygame
from pyvidplayer2 import (READER_IMAGEIO, Video, VideoPlayer, VideoPyglet,
                          VideoPyQT, VideoPySide, VideoTkinter, VideoWx,
                          VideoRaylib)

from test_video import VIDEO_PATH
from test_youtube import YOUTUBE_PATH


@unittest.skipIf(sys.platform.startswith("linux") or
                 sys.platform == "darwin", "Don't work well on linux or mac")
class TestPreviews(unittest.TestCase):
    # tests that looping is seamless
    # also tests that video does indeed loop by timing out otherwise
    def test_seamless_loop(self):
        v = Video("resources/loop.mp4")
        vp = VideoPlayer(v, (0, 0, v.original_size[0], v.original_size[1]), loop=True)

        self.assertTrue(v._buffer_first_chunk)

        end_of_video = False
        stop_loop = False

        def modified_preview():
            nonlocal end_of_video, stop_loop

            win = pygame.display.set_mode(vp.frame_rect.size, pygame.RESIZABLE)
            v.play()
            stop = False
            while not stop:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        v.stop()
                        stop = True
                vp.update(events, False, 60)
                vp.draw(win)

                if end_of_video:
                    if v.frame_surf is None:
                        stop_loop = True
                        break
                    else:
                        end_of_video = False
                elif v.frame == 60:
                    end_of_video = True

                pygame.display.update()
            pygame.display.quit()
            vp.close()

        thread = Thread(target=modified_preview)
        thread.start()

        t = 0
        track = False
        buffers = []
        timeout = time.time()
        while not stop_loop:
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

        # preview stopped unexpectedly because these are None
        if stop_loop:
            self.assertIsNotNone(v.frame_data)
            self.assertIsNotNone(v.frame_surf)

        vp.close()

    # tests for a bug where previews would never end if video was looping
    # inconsistent test, may never terminate
    @unittest.skip
    def test_looping_preview(self):
        # for some reason, this fails if ran with the rest, but passes when ran individually
        # pygame.quit()
        # pygame.init()

        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, v.original_size[0], v.original_size[1]), loop=True)

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

    # tests video player preview works and does not close when video ends
    def test_video_player_preview(self):
        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, 1280, 720), interactable=True)
        v.seek(v.duration - 3)
        thread = Thread(target=lambda: vp.preview())
        thread.start()
        time.sleep(5)
        self.assertTrue(thread.is_alive())
        self.assertFalse(vp.closed)
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        thread.join()

    # tests that video players work with youtube videos
    def test_youtube_player(self):
        v = Video(YOUTUBE_PATH, youtube=True)
        vp = VideoPlayer(v, (0, 0, v.original_size[0], v.original_size[1]))
        v.seek(v.duration - 1)
        thread = Thread(target=lambda: vp.preview())
        thread.start()
        time.sleep(5)
        self.assertTrue(thread.is_alive())
        self.assertFalse(vp.closed)
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        thread.join()

    # tests video preview with Youtube
    def test_youtube_preview(self):
        v = Video(YOUTUBE_PATH, youtube=True)
        v.seek(v.duration - 1)
        thread = Thread(target=lambda: v.preview())
        thread.start()
        time.sleep(5)
        self.assertFalse(thread.is_alive())
        self.assertTrue(v.closed)
        thread.join()

    # tests that previews start from where the video position is, and that they close the video afterwards
    def test_previews(self):
        for lib in (
            Video,
            VideoTkinter,
            VideoPyglet,
            # VideoRaylib cannot run alongside pyglet anymore
            VideoPyQT,
            VideoPySide,
            VideoWx
        ):
            v = lib(VIDEO_PATH)
            v.seek(v.duration - 0.1)
            if lib == Video:
                v.preview(show_fps=True)
            else:
                v.preview()
            self.assertTrue(v.closed)
            v.close()

    # tests raylib separately, because for some reason it cannot be
    # paired with pyglet
    @unittest.skip
    def test_raylib(self):
        with VideoRaylib(VIDEO_PATH) as v:
            v.seek(v.duration - 0.1)
            v.preview()
        # raylib overrides close method
        self.assertTrue(v.closed)

    # tests pyav dependency message
    def test_imageio_needs_pyav(self):
        # mocks away av
        dict_ = {key: None for key in sys.modules.keys() if key.startswith("av.")}
        dict_.update({"av": None})
        with unittest.mock.patch.dict("sys.modules", dict_):
            with self.assertRaises(ImportError) as _:
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
