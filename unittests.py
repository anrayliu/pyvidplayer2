# full unit tests for pyvidplayer2 v0.9.25
# takes around 10 minutes to run all of them

import math
import random
import unittest
from random import uniform
from threading import Thread

import numpy as np
import pygame
import os
import time
import cv2
import yt_dlp
import yt_dlp.utils
from sounddevice import query_devices
from pyvidplayer2 import *
import pyvidplayer2._version


def get_videos():
    paths = []
    for file in os.listdir("resources"):
        for ext in ("mp4", "avi", "webm", "mov", "mkv"):
            if file.endswith(ext):
                paths.append(os.path.join("resources", file))
    return paths

def check_same_frames(f1, f2):
    return np.array_equal(f1, f2)

def timed_loop(seconds, func):
    t = time.time() + seconds
    while time.time() < t:
        time.sleep(0.1)
        func()

def while_loop(condition_func, func, timeout):
    t = time.time()
    while condition_func():
        time.sleep(0.1)
        func()
        if time.time() - t > timeout:
            raise RuntimeError("Loop timed out.")

def get_youtube_urls(max_results=5):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info("https://www.youtube.com/feed/trending", download=False)

    if "entries" in info:
        return [entry["url"] for entry in info["entries"] if "view_count" in entry][:max_results]
    else:
        raise RuntimeError("Could not extract youtube urls.")

def find_device(*lambdas):
    for device in query_devices():
        passed = True
        for func in lambdas:
            if not func(device):
                passed = False
        if passed:
            return device["index"]

    raise RuntimeError("Could not find specified sound device.")

PATHS = get_videos()
PATHS.remove("resources\\nov.mp4") # ruins a lot of tests
VIDEO_PATH = "resources\\trailer1.mp4"
YOUTUBE_PATH = "https://www.youtube.com/watch?v=K8PoK3533es&t=3s"

SUBS = (
    (0.875, 1.71, "Oh, my God!"),
    (5.171, 5.88, "Hang on!"),
    (6.297, 8.383, "- Ethan!\n- Go, go, go!"),
    (8.383, 11.761, "Audiences and critics can't believe\nwhat they're seeing."),
    (14.139, 15.015, "Listen to me."),
    (15.015, 16.85, "The world's coming after you."),
    (16.85, 18.101, "Stay out of my way."),
    (18.935, 21.187, "“Tom Cruise has outdone himself.”"),
    (22.105, 25.025, "With a 99% on Rotten Tomatoes."),
    (25.025, 25.483, "Yes!"),
    (25.483, 29.446, "“Mission: Impossible - Dead Reckoning is filled with ‘holy shit’ moments.”"),
    (29.446, 30.488, "What is happening?"),
    (30.488, 32.49, "“This is why we go to the movies.”"),
    (33.908, 35.577, "Oh, I like her."),
    (35.577, 37.287, "“It's pulse pounding.”"),
    (37.746, 39.622, "“It will rock your world.”"),
    (40.081, 41.875, "With “jaw dropping action.”"),
    (43.209, 44.085, "Is this where we run?"),
    (44.085, 44.919, "Go, go, go, go!"),
    (45.253, 45.92, "Probably."),
    (46.421, 49.132, "“It's one of the best action movies\never made.”"),
    (49.466, 50.508, "What more can I say?"),
    (50.925, 54.888, "“See it in the biggest, most seat-shaking theater you can find.”"),
    (55.138, 57.891, "“It will take your breath away.”"),
    (58.808, 59.893, "Ethan, did you make it?"),
    (59.893, 60.852, "Are you okay?")
)


class TestVideo(unittest.TestCase):
    def setUp(self):
        self.static_video = Video("resources\\clip.mp4")
        self.static_player = VideoPlayer(self.static_video, (0, 0, *self.static_video.original_size))
        self.static_webcam = Webcam()

    def tearDown(self):
        self.static_video.close()
        self.static_player.close()
        self.static_webcam.close()

    # tests that each chunk setting is working properly
    def test_chunk_settings(self):
        # check that first frame is read correctly
        v1 = Video(VIDEO_PATH, chunk_size=15)
        original_frame = next(v1)
        v2 = Video(VIDEO_PATH, chunk_size=10, max_chunks=5, max_threads=3)
        new_frame = next(v2)
        self.assertTrue(check_same_frames(original_frame, new_frame))

        # check that first thread started
        v1.update()
        self.assertEqual(len(v1._threads), 1)
        v2.update()
        self.assertEqual(len(v2._threads), 1)

        # check that second thread is handled properly
        v1.update()
        self.assertEqual(len(v1._threads), 1)
        v2.update()
        self.assertEqual(len(v2._threads), 2)

        # check that third thread is handled properly
        v1.update()
        self.assertEqual(len(v1._threads), 1)
        v2.update()
        self.assertEqual(len(v2._threads), 3)

        # check that fourth thread is handled properly
        v1.update()
        self.assertEqual(len(v1._threads), 1)
        v2.update()
        self.assertEqual(len(v2._threads), 3)

        # update both videos for 5 seconds
        timed_loop(3, lambda: (v1.update(), v2.update()))

        # check for number of stored chunks
        self.assertEqual(len(v1._chunks), 1)
        self.assertEqual(len(v2._chunks), 5)

        v1.close()
        v2.close()

    # tests each post processing function
    def test_post_processing(self):
        # must be done with clip.mp4 because trailer1.mp4 fails letterbox due to it already having one
        # and trailer2.mp4 fails noise due to the black opening frames

        v1 = Video("resources/clip.mp4")
        original_frame = next(v1)
        v2 = Video("resources/clip.mp4")
        new_frame = next(v2)
        self.assertTrue(check_same_frames(original_frame, new_frame))

        for func in (lambda d: np.fliplr(d), PostProcessing.blur, PostProcessing.sharpen, PostProcessing.greyscale, PostProcessing.noise, PostProcessing.letterbox, PostProcessing.cel_shading, PostProcessing.flipup, PostProcessing.fliplr):
            v2.set_post_func(func)
            self.assertFalse(check_same_frames(next(v1), next(v2)))

        v1.close()
        v2.close()

    # tests metadata accuracy for 3 main types of videos
    def test_metadata(self):
        v = Video("resources\\trailer1.mp4")
        self.assertEqual(v.path, "resources\\trailer1.mp4")
        self.assertEqual(v._audio_path, "resources\\trailer1.mp4")
        self.assertEqual(v.name, "trailer1")
        self.assertEqual(v.ext, ".mp4")
        self.assertEqual(v.duration, 67.27554166666665)
        self.assertEqual(v.frame_count, 1613)
        self.assertEqual(v.frame_rate, 23.976023976023978)
        self.assertEqual(v.original_size, (1280, 720))
        self.assertEqual(v.current_size, (1280, 720))
        self.assertEqual(v.aspect_ratio, 1.7777777777777777)
        self.assertEqual(type(v._vid).__name__, "CVReader")
        v.close()

        v = Video(YOUTUBE_PATH, youtube=True)
        self.assertTrue(v.path.startswith("https"))
        self.assertTrue(v._audio_path.startswith("https"))
        self.assertEqual(v.name, "The EASIEST Way to Play Videos in Pygame/Python!")
        self.assertEqual(v.ext, ".webm")
        self.assertEqual(v.duration, 69.36666666666666)
        self.assertEqual(v.frame_count, 2081)
        self.assertEqual(v.frame_rate, 30.0)
        self.assertEqual(v.original_size, (1920, 1080))
        self.assertEqual(v.current_size, (1920, 1080))
        self.assertEqual(v.aspect_ratio, 1.7777777777777777)
        self.assertEqual(type(v._vid).__name__, "CVReader")
        v.close()

        with open("resources\\trailer1.mp4", "rb") as file:
            v = Video(file.read())
        self.assertTrue(type(v.path) == bytes)
        self.assertEqual(v._audio_path, "-")
        self.assertEqual(v.name, "")
        self.assertEqual(v.ext, "")
        self.assertEqual(v.duration, 67.275542)
        self.assertEqual(v.frame_count, 1613)
        self.assertEqual(v.frame_rate, 23.976023976023978)
        self.assertEqual(v.original_size, (1280, 720))
        self.assertEqual(v.current_size, (1280, 720))
        self.assertEqual(v.aspect_ratio, 1.7777777777777777)
        self.assertEqual(type(v._vid).__name__, "IIOReader")
        v.close()

    # test the set_interp method
    def test_set_interp(self):
        v = Video(VIDEO_PATH, interp="linear")
        self.assertEqual(v.interp, cv2.INTER_LINEAR)
        v.close()
        v = Video(VIDEO_PATH, interp="cubic")
        self.assertEqual(v.interp, cv2.INTER_CUBIC)
        v.close()
        v = Video(VIDEO_PATH, interp="area")
        self.assertEqual(v.interp, cv2.INTER_AREA)
        v.close()
        v = Video(VIDEO_PATH, interp="lanczos4")
        self.assertEqual(v.interp, cv2.INTER_LANCZOS4)
        v.close()
        v = Video(VIDEO_PATH, interp="nearest")
        self.assertEqual(v.interp, cv2.INTER_NEAREST)

        v.set_interp("linear")
        self.assertEqual(v.interp, cv2.INTER_LINEAR)
        v.set_interp("cubic")
        self.assertEqual(v.interp, cv2.INTER_CUBIC)
        v.set_interp("area")
        self.assertEqual(v.interp, cv2.INTER_AREA)
        v.set_interp("lanczos4")
        self.assertEqual(v.interp, cv2.INTER_LANCZOS4)
        v.set_interp("nearest")
        self.assertEqual(v.interp, cv2.INTER_NEAREST)

        v.set_interp(cv2.INTER_LINEAR)
        self.assertEqual(v.interp, cv2.INTER_LINEAR)
        v.set_interp(cv2.INTER_CUBIC)
        self.assertEqual(v.interp, cv2.INTER_CUBIC)
        v.set_interp(cv2.INTER_AREA)
        self.assertEqual(v.interp, cv2.INTER_AREA)
        v.set_interp(cv2.INTER_LANCZOS4)
        self.assertEqual(v.interp, cv2.INTER_LANCZOS4)
        v.set_interp(cv2.INTER_NEAREST)
        self.assertEqual(v.interp, cv2.INTER_NEAREST)

        self.assertRaises(ValueError, v.set_interp, "unrecognized interp")

        w = Webcam(interp="lanczos4")
        self.assertEqual(w.interp, cv2.INTER_LANCZOS4)
        w.set_interp("lanczos4")
        self.assertEqual(w.interp, cv2.INTER_LANCZOS4)
        w.set_interp(cv2.INTER_LANCZOS4)
        self.assertEqual(w.interp, cv2.INTER_LANCZOS4)
        self.assertRaises(ValueError, w.set_interp, "unrecognized interp")

        w.close()
        v.close()

    # tests that each file can be opened and recognized as bytes
    def test_detect_as_bytes(self):
        for file in PATHS:
            with open(file, "rb") as f:
                v = Video(f.read())
                self.assertTrue(v.as_bytes, f"{file} failed unit test")
                v.close()

    # tests seeking, requires an accurate frame_count attribute
    def test_seeking(self):
        for file in PATHS:
            if file.endswith(".webm"):
                continue

            v = Video(file)
            v.probe() # get accurate frame count

            # testing relative time seek
            v.seek(2, relative=False)

            self.assertEqual(v.get_pos(), 2.0)

            FRAME = int(2 * v.frame_rate)

            self.assertEqual(v.frame, FRAME)
            original_frame = next(v)

            # testing non relative time seek
            v.seek(0, relative=False)
            self.assertEqual(v.get_pos(), 0.0)
            self.assertEqual(v.frame, 0)

            # testing non relative frame seek
            v.seek_frame(FRAME)
            self.assertEqual(v.get_pos(), FRAME / v.frame_rate)
            self.assertEqual(v.frame, FRAME)

            new_frame = next(v)

            self.assertTrue(check_same_frames(original_frame, new_frame))

            # testing relative frame seek
            v.seek_frame(-FRAME, relative=True)
            self.assertEqual(v.get_pos(), 1 / v.frame_rate)
            self.assertEqual(v.frame, 1)

            # testing lower bound
            v.seek(-1, relative=False)
            self.assertEqual(v.get_pos(), 0.0)
            self.assertEqual(v.frame, 0)

            # testing upper bound
            v.seek(v.duration)

            # should never raise a stop iteration exception
            original_frame = next(v)
            v.seek(v.duration)

            self.assertEqual(v.get_pos(), v.duration)
            self.assertEqual(v.frame, v.frame_count - 1)

            v.seek_frame(v.frame_count)

            # should never raise a stop iteration exception
            new_frame = next(v)
            v.seek_frame(v.frame_count)

            self.assertEqual(v.get_pos(), (v.frame_count - 1) / v.frame_rate)
            self.assertEqual(v.frame, v.frame_count - 1)

            self.assertTrue(check_same_frames(original_frame, new_frame))

            # tests that when seeking to x, exactly x will be obtained when checking-
            for i in range(5):
                rand_time = random.uniform(0, v.duration)
                v.seek(rand_time, relative=False)
                self.assertEqual(v.get_pos(), rand_time)

                rand_frame = random.randrange(0, v.frame_count)
                v.seek_frame(rand_frame, relative=False)
                self.assertEqual(v.frame, rand_frame)

            v.close()

    # test __len__
    def test_magic_method_len(self):
        self.assertEqual(self.static_video.frame_count, len(self.static_video))

    # test __str__
    def test_magic_method_str(self):
        self.assertEqual("<VideoPygame(path=resources\\clip.mp4)>", str(self.static_video))
        s = Subtitles("resources\\subs1.srt")
        self.assertEqual("<Subtitles(path=resources\\subs1.srt)>", str(s))
        vp = VideoPlayer(self.static_video, (0, 0, *self.static_video.original_size))
        self.assertEqual("<VideoPlayer(path=resources\\clip.mp4)>", str(vp))
        w = Webcam()
        self.assertEqual("<Webcam(fps=30)>", str(w))
        w.close()

    # test if subs are initialized correctly
    def test_init_subs(self):
        v = Video("resources/trailer1.mp4")
        self.assertEqual(v.subs, [])
        v.close()

        s = Subtitles("resources/subs1.srt")
        v = Video("resources/trailer1.mp4", subs=s)
        self.assertEqual(v.subs, [s])
        v.close()

        v = Video("resources/trailer1.mp4", subs=[s, s, s])
        self.assertEqual(v.subs, [s, s, s])

        v.set_subs(None)
        self.assertEqual(v.subs, [])
        v.set_subs([])
        self.assertEqual(v.subs, [])
        v.set_subs(s)
        self.assertEqual(v.subs, [s])
        v.set_subs([s, s, s])
        self.assertEqual(v.subs, [s, s, s])

        v.close()

    # test video active behaviour
    def test_active(self):
        v = Video(VIDEO_PATH)
        self.assertTrue(v.active)
        v.resume()
        self.assertTrue(v.active)
        v.pause()
        self.assertTrue(v.active)
        v.resume()
        self.assertTrue(v.active)
        v.stop()
        self.assertFalse(v.active)
        v.stop()
        self.assertFalse(v.active)
        v.play()
        self.assertTrue(v.active)
        v.play()
        self.assertTrue(v.active)
        # plays video until end
        v.seek(v.duration)
        while_loop(lambda: v.active, v.update, 10)
        self.assertFalse(v.active)
        v.stop()
        self.assertFalse(v.active)
        v.play()
        self.assertTrue(v.active)
        v.close()

    # test that video stops correctly
    def test_stop(self):
        v = Video(VIDEO_PATH)
        while_loop(lambda: v.frame < 10, v.update, 10)
        v.stop()
        self.assertFalse(v.active)
        self.assertIs(v.frame_data, None)
        self.assertIs(v.frame_surf, None)
        self.assertFalse(v.paused)
        v.stop() # test for exception
        v.close()

    # tests that set_speed is deprecated
    def test_set_speed_method(self):
        self.assertRaises(DeprecationWarning, self.static_video.set_speed, 1.0)

    # tests that preloading frames is done properly
    def test_preloaded_frames(self):
        v = Video("resources\\clip.mp4")
        self.assertFalse(v._preloaded)
        timed_loop(2, v.update)
        frame = v.frame
        v._preload_frames()
        self.assertTrue(v._preloaded)

        # checks that preloading does not change the current frame
        self.assertEqual(v._vid.frame, frame)

        self.assertEqual(len(v._preloaded_frames), v.frame_count)
        v.restart()
        for i, frame in enumerate(v):
            self.assertTrue(check_same_frames(v._preloaded_frames[i], frame))
        v.close()

        self.assertTrue(v._preloaded)

    # tests cv2 frame count, proving frame count, and real frame count
    def test_frame_counts(self):
        for file in PATHS:
            v = Video(file)
            # check that header information was not completely wrong
            self.assertGreater(v.frame_count, 0)
            self.assertGreater(v.frame_rate, 0)
            self.assertGreater(v.duration, 0)

            v.frame_count = 0
            v.frame_rate = 0
            v.frame_delay = 0
            v.duration = 0
            v.original_size = (0, 0)
            v.aspect_ratio = 1

            v.probe()
            real = v._get_real_frame_count()
            self.assertEqual(v.frame_count, real, f"{file} failed unit test")
            self.assertGreater(v.frame_rate, 0)
            self.assertEqual(v.frame_delay, 1 / v.frame_rate)
            self.assertGreater(v.duration, 0)
            self.assertNotEqual(v.original_size, (0, 0))
            self.assertEqual(v.aspect_ratio, v.original_size[0] / v.original_size[1])

            self.assertEqual(real, len(v._get_all_pts()))

            v.close()

    # tests the convert seconds method
    def test_convert_seconds(self):
        v = self.static_video

        # Whole Hours
        self.assertEqual(v._convert_seconds(3600), "1:0:0.0")
        self.assertEqual(v._convert_seconds(7200), "2:0:0.0")

        # Hours and Minutes
        self.assertEqual(v._convert_seconds(3660), "1:1:0.0")
        self.assertEqual(v._convert_seconds(7325), "2:2:5.0")

        # Minutes and Seconds
        self.assertEqual(v._convert_seconds(65), "0:1:5.0")
        self.assertEqual(v._convert_seconds(125), "0:2:5.0")

        # Seconds Only
        self.assertEqual(v._convert_seconds(5), "0:0:5.0")
        self.assertEqual(v._convert_seconds(59), "0:0:59.0")

        # Fractional Seconds
        self.assertEqual(v._convert_seconds(5.3), "0:0:5.3")
        self.assertEqual(v._convert_seconds(125.6), "0:2:5.6")
        self.assertEqual(v._convert_seconds(7325.9), "2:2:5.9")

        # Zero Seconds
        self.assertEqual(v._convert_seconds(0), "0:0:0.0")

        # Large Number
        self.assertEqual(v._convert_seconds(86400), "24:0:0.0")
        self.assertEqual(v._convert_seconds(90061.5), "25:1:1.5")

        # Negative Seconds
        self.assertEqual(v._convert_seconds(-5), "0:0:5.0")
        self.assertEqual(v._convert_seconds(-3665), "1:1:5.0")

    # tests that videos are closed properly
    def test_closed(self):
        v = Video(VIDEO_PATH)
        self.assertFalse(v.closed)
        self.assertFalse(v._audio.loaded)
        self.assertFalse(v._vid.released)
        while_loop(lambda: not v._audio.loaded, v.update, 10)
        self.assertFalse(v.closed)
        self.assertTrue(v._audio.loaded)
        self.assertFalse(v._vid.released)
        v.stop()
        self.assertFalse(v.closed)
        self.assertFalse(v._audio.loaded)
        self.assertFalse(v._vid.released)
        v.close()
        self.assertTrue(v.closed)
        self.assertFalse(v._audio.loaded)
        self.assertTrue(v._vid.released)
        v.close() # check for exception

    # test opens the first 5 trending youtube videos
    def test_youtube(self):
        for url in get_youtube_urls():
            v = Video(url, youtube=True)
            self.assertTrue(v._audio_path.startswith("https"))
            self.assertTrue(v.path.startswith("https"))
            while_loop(lambda: v.get_pos() < 1, v.update, 10)
            v.close()

    # test that youtube chunk settings are checked
    def test_youtube_settings(self):
        v = Video(YOUTUBE_PATH, youtube=True, chunk_size=30, max_threads=3, max_chunks=3)
        self.assertEqual(v.chunk_size, 60)
        self.assertEqual(v.max_threads, 1)
        self.assertEqual(v.max_chunks, 3)
        v.close()

    # test common resolutions
    def test_change_resolution(self):
        v = self.static_video

        # ensures no actual resampling is taking place
        self.assertIs(v.frame_surf, None)

        SIZE = v.current_size
        v.change_resolution(144)
        self.assertEqual(v.current_size, (256, 144))
        v.change_resolution(240)
        self.assertEqual(v.current_size, (426, 240))
        v.change_resolution(360)
        self.assertEqual(v.current_size, (640, 360))
        v.change_resolution(480)
        self.assertEqual(v.current_size, (854, 480))
        v.change_resolution(720)
        self.assertEqual(v.current_size, (1280, 720))
        v.change_resolution(1080)
        self.assertEqual(v.current_size, (1920, 1080))
        v.change_resolution(1440)
        self.assertEqual(v.current_size, (2560, 1440))
        v.change_resolution(2160)
        self.assertEqual(v.current_size, (3840, 2160))
        v.change_resolution(4320)
        self.assertEqual(v.current_size, (7680, 4320))
        v.resize(SIZE)

    # test that speed is properly capped
    def test_speed_limit(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(v.speed, 1.0)
        self.assertEqual(v.get_speed(), 1.0)
        v.close()
        v = Video(VIDEO_PATH, speed=2.0)
        self.assertEqual(v.speed, 2.0)
        v.close()
        v = Video(VIDEO_PATH, speed=0)
        self.assertEqual(v.speed, 0.25)
        v.close()
        v = Video(VIDEO_PATH, speed=100)
        self.assertEqual(v.speed, 10.0)
        v.close()

    # tests that a video can be played entirely without issues
    def test_full_playback(self):
        v = Video("resources\\clip.mp4")
        while_loop(lambda: v.active, v.update, 10)
        v.close()

    # tests that a video can be played entirely in a video player
    def test_full_player(self):
        v = Video("resources\\clip.mp4")
        vp = VideoPlayer(v, (0, 0, *v.original_size))
        while_loop(lambda: v.active, vp.update, 10)
        vp.close()
        self.assertTrue(vp.closed)

    # test each graphics library
    def test_previews(self):
        for video in (Video, VideoTkinter, VideoPyglet, VideoPyQT, VideoPySide, VideoRaylib):
            print(video.__name__)
            v = video("resources\\clip.mp4")
            v.preview()

    # tests youtube max_res parameter
    def test_max_resolution(self):
        for res in (144, 360, 720, 1080):
            v = Video(YOUTUBE_PATH, youtube=True, max_res=res)
            self.assertEqual(v.current_size[1], res)
            v.close()
            time.sleep(0.1) # prevents spamming youtube

    # tests that high frame rate videos can be achieved
    def test_unlocked_fps(self):
        for audio_handler in (True, False):
            v = Video("resources\\100fps.mp4", use_pygame_audio=audio_handler)
            seconds_elapsed = 0
            clock = pygame.time.Clock()
            v.play()
            timer = 0
            frames = 0
            passed = False
            while v.active and seconds_elapsed < 10:
                dt = clock.tick(0)
                timer += dt
                if timer >= 1000:
                    seconds_elapsed += 1
                    if frames > 80:    # 80% of the maximum frame rate
                        passed = True
                        break
                    timer = 0
                    frames = 0
                if v.update():
                    frames += 1
            v.close()
            self.assertTrue(passed)

    # tests that pausing works correctly
    def test_pausing(self):
        # repeat test for pyaudio and pygame mixer
        for audio_handler in (False, True):
            v = Video(VIDEO_PATH, use_pygame_audio=audio_handler)

            # not paused on creation
            self.assertFalse(v.paused)
            self.assertFalse(v.get_paused())

            # loads first chunk of audio
            while_loop(lambda: not v._audio.loaded, v.update, 10)

            v.resume()
            self.assertFalse(v.paused)
            v.pause()
            self.assertTrue(v.paused)
            v.pause()
            self.assertTrue(v.paused)

            if v.use_pygame_audio:
                self.assertFalse(pygame.mixer.music.get_busy())
            else:
                self.assertTrue(v._audio.paused)

            v.resume()
            self.assertFalse(v.paused)
            if v.use_pygame_audio:
                self.assertTrue(pygame.mixer.music.get_busy())
            else:
                self.assertFalse(v._audio.paused)
            v.pause()

            # rewinding because some audio may have been played during loading
            v.seek(0)
            self.assertTrue(v.paused)

            frame = v.frame
            timed_loop(3, v.update)
            self.assertEqual(frame, v.frame)

            v.toggle_pause()
            self.assertFalse(v.paused)
            v.toggle_pause()
            self.assertTrue(v.paused)

            v.close()

    # tests muting works correctly
    def test_mute(self):
        for audio_handler in (False, True):
            v = Video(VIDEO_PATH, use_pygame_audio=audio_handler)
            self.assertFalse(v.muted)
            self.assertFalse(v._audio.muted)
            v.unmute()
            self.assertFalse(v.muted)
            self.assertFalse(v._audio.muted)
            v.mute()
            self.assertTrue(v.muted)
            self.assertTrue(v._audio.muted)
            v.mute()
            self.assertTrue(v.muted)
            self.assertTrue(v._audio.muted)
            v.toggle_mute()
            self.assertFalse(v.muted)
            self.assertFalse(v._audio.muted)
            v.toggle_mute()
            self.assertTrue(v.muted)
            self.assertTrue(v._audio.muted)

            while_loop(lambda: v.frame < 10, v.update, 10)

            if v.use_pygame_audio:
                self.assertEqual(pygame.mixer.music.get_volume(), 0)
            else:
                self.assertFalse(np.any(v._audio._buffer))

            v.close()

    # tests that silent videos are detected
    def test_no_audio_detection(self):
        for file in PATHS:
            v = Video(file)
            self.assertEqual(v.no_audio, v.name in ("60fps", "silent", "hdr", "test"), f"{file} failed unit test")
            v.close()

    # tests cv2 and ffmepg resamplers work as intended
    def test_resampling(self):
        v = Video(VIDEO_PATH)
        original_frame = next(v)

        NEW_SIZE = v.original_size[0] // 2, v.original_size[1] // 2

        # ensures both resamplers are active
        cv_resampled = v._resize_frame(original_frame, NEW_SIZE, cv2.INTER_CUBIC, False)
        ffmpeg_resampled = v._resize_frame(original_frame, NEW_SIZE, "bicubic", True)
        self.assertFalse(check_same_frames(cv_resampled, ffmpeg_resampled))

        SIZES = ((426, 240), (640, 360), (854, 480), (1280, 720), (1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320))

        # test cv resamplers
        for size in SIZES:
            for flag in (cv2.INTER_LINEAR, cv2.INTER_NEAREST, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4, cv2.INTER_AREA):
                new_frame = v._resize_frame(original_frame, size, flag, False)
                webcam_resized = self.static_webcam._resize_frame(original_frame, size, flag)
                self.assertTrue(check_same_frames(new_frame, webcam_resized))
                self.assertEqual(new_frame.shape, (size[1], size[0], 3))
                if size == v.original_size:     # check that no resizing occurred
                   self.assertTrue(check_same_frames(original_frame, new_frame))

        # test ffmpeg resamplers
        for size in SIZES:
            for flag in ("bilinear", "bicubic", "neighbor", "area", "lanczos", "fast_bilinear", "gauss", "spline"):
                new_frame = v._resize_frame(original_frame, size, flag, True)
                self.assertEqual(new_frame.shape, (size[1], size[0], 3))
                if size == v.original_size:     # check that no resizing occurred
                    self.assertTrue(check_same_frames(original_frame, new_frame))

        # test no cv
        for size in SIZES:
            for flag in (cv2.INTER_LINEAR, cv2.INTER_NEAREST, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4, cv2.INTER_AREA):
                new_frame = v._resize_frame(original_frame, size, flag, True)
                self.assertEqual(new_frame.shape, (size[1], size[0], 3))
                if size == v.original_size:
                    self.assertTrue(check_same_frames(original_frame, new_frame))

        v.resize(NEW_SIZE)
        while_loop(lambda: v.frame < 10, v.update, 5)
        self.assertEqual(v.frame_surf.get_size(), NEW_SIZE)

        v.close()

    # tests that subtitles are properly read and displayed
    def test_subtitles(self):
        for yt in (True, False):
            # running video in x5 to speed up test
            v = Video("https://www.youtube.com/watch?v=HurjfO_TDlQ" if yt else "resources\\trailer1.mp4", subs=Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ" if yt else "resources\\subs1.srt", youtube=yt, pref_lang="en-US"), speed=5, youtube=yt)

            def check_subs():
                v.update()

                timestamp = v.frame / v.frame_rate
                # skip when frame has not been rendered yet
                if timestamp == 0:
                    return

                in_interval = False
                for start, end, text in SUBS:
                    if start <= timestamp <= end:
                        in_interval = True
                        self.assertEqual(check_same_frames(pygame.surfarray.array3d(v.frame_surf), pygame.surfarray.array3d(v._create_frame(
                            v.frame_data))), v.subs_hidden)

                        # check the correct subtitle was generated
                        if not v.subs_hidden:
                            self.assertTrue(check_same_frames(pygame.surfarray.array3d(v.subs[0]._to_surf(text)), pygame.surfarray.array3d(v.subs[0].surf)))

                if not in_interval:
                    self.assertTrue(
                        check_same_frames(pygame.surfarray.array3d(v.frame_surf), pygame.surfarray.array3d(v._create_frame(
                            v.frame_data))))

            self.assertFalse(v.subs_hidden)

            def randomized_test():
                rand = random.randint(1, 3)
                if v.subs_hidden:
                    v.show_subs()
                    self.assertFalse(v.subs_hidden)
                else:
                    v.hide_subs()
                    self.assertTrue(v.subs_hidden)
                timed_loop(rand, check_subs)

            # test playback while turning on and off subs
            while_loop(lambda: v.active, randomized_test, 120)

            if not yt:
                # test that seeking works for subtitles
                for i in range(3):
                    v.seek(random.uniform(0, v.duration), relative=False)
                    v.play()
                    timed_loop(1, v.update)

            v.close()

    # tests opening a youtube video with bad paths
    def test_open_youtube(self):
        with self.assertRaises(YTDLPError) as context:
            Video(VIDEO_PATH, youtube=True)
        self.assertEqual(str(context.exception), "yt-dlp could not open video. Please ensure the URL is a valid Youtube video.")
        time.sleep(0.1)

        with self.assertRaises(YTDLPError) as context:
            Video(YOUTUBE_PATH, youtube=True, max_res=0)
        self.assertEqual(str(context.exception), "Could not find requested resolution.")
        time.sleep(0.1)

        with self.assertRaises(YTDLPError) as context:
            Video("https://www.youtube.com/watch?v=thisvideodoesnotexistauwdhoiawdhoiawhdoih", youtube=True)
        self.assertEqual(str(context.exception), "yt-dlp could not open video. Please ensure the URL is a valid Youtube video.")

    # tests appropriate error messages when opening subtitles
    def test_open_subtitles(self):
        Subtitles("resources/subs1.srt")

        # ffprobe can also read subtitle files
        Subtitles("resources/subs1.srt", track_index=0)

        with self.assertRaises(SubtitleError) as context:
            Subtitles("resources/subs1.srt", track_index=1)
        self.assertEqual(str(context.exception), "Could not find selected subtitle track in video.")

        with self.assertRaises(SubtitleError) as context:
            Subtitles("resources/fake.txt")
        self.assertEqual(str(context.exception), "Could not load subtitles. Unknown format or corrupt file. Check that the proper encoding format is set.")

        with self.assertRaises(SubtitleError) as context:
            Subtitles("resources/fake.txt", track_index=0)
        self.assertEqual(str(context.exception), "Could not find selected subtitle track in video.")

        with self.assertRaises(SubtitleError) as context:
            Subtitles("resources/wSubs.mp4")
        self.assertEqual(str(context.exception), "Could not load subtitles. Unknown format or corrupt file. Check that the proper encoding format is set.")

        Subtitles("resources/wSubs.mp4", track_index=0)

        with self.assertRaises(SubtitleError) as context:
            Subtitles("resources/wSubs.mp4", track_index=1)
        self.assertEqual(str(context.exception), "Could not find selected subtitle track in video.")

        with self.assertRaises(SubtitleError) as context:
            Subtitles("resources/trailer1.mp4")
        self.assertEqual(str(context.exception), "Could not load subtitles. Unknown format or corrupt file. Check that the proper encoding format is set.")

        with self.assertRaises(SubtitleError) as context:
            Subtitles("resources/trailer1.mp4", track_index=1)
        self.assertEqual(str(context.exception), "Could not find selected subtitle track in video.")

        with self.assertRaises(FileNotFoundError):
            Subtitles("resources\\badpath")

        with self.assertRaises(FileNotFoundError) as context:
            Subtitles("resources\\badpath", track_index=0)
        self.assertEqual(str(context.exception), "[Errno 2] No such file or directory: 'resources\\badpath'")

        with self.assertRaises(FileNotFoundError) as context:
            Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ")
        self.assertEqual(str(context.exception), "[Errno 2] No such file or directory: 'https://www.youtube.com/watch?v=HurjfO_TDlQ'")

        with self.assertRaises(FileNotFoundError) as context:
            Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ", track_index=0)
        self.assertEqual(str(context.exception), "[Errno 2] No such file or directory: 'https://www.youtube.com/watch?v=HurjfO_TDlQ'")

        with self.assertRaises(SubtitleError) as context:
            Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ", youtube=True)
        self.assertEqual(str(context.exception), "Could not find subtitles in the specified language.")
        time.sleep(0.1)

        s = Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ", youtube=True, pref_lang="en-US")
        self.assertFalse(s._auto_cap)
        time.sleep(0.1)

        s = Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ", youtube=True, pref_lang="zh-Hant-en-US")
        self.assertTrue(s._auto_cap)
        time.sleep(0.1)

        with self.assertRaises(SubtitleError) as context:
            Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ", youtube=True, pref_lang="badcode")
        self.assertEqual(str(context.exception), "Could not find subtitles in the specified language.")
        time.sleep(0.1)

        with self.assertRaises(SubtitleError) as context:
            Subtitles(YOUTUBE_PATH, youtube=True, pref_lang="badcode")
        self.assertEqual(str(context.exception), "Could not find subtitles in the specified language.")
        time.sleep(0.1)

        # ffprobe can read extracted subtitle file
        Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ", youtube=True, track_index=0, pref_lang="en-US")
        time.sleep(0.1)

        for url in ("https://www.youtube.com/@joewoobie1155", "https://www.youtube.com/channel/UCY3Rgenpuy4cY79eGk6DmuA", "https://www.youtube.com/"):
            with self.assertRaises(SubtitleError) as context:
                Subtitles(url, youtube=True)
            self.assertEqual(str(context.exception), "Could not find subtitles in the specified language.")
        time.sleep(0.1)

        with self.assertRaises(yt_dlp.utils.DownloadError):
            Subtitles("https://www.youtube.com/shorts", youtube=True)

    # tests correct errors are raised when given bad input paths
    def test_open_video(self):
        self.assertRaises(OpenCVError, lambda: Video("resources\\fake.txt"))
        self.assertRaises(FileNotFoundError, lambda: Video("badpath"))

    # tests that subtitle tracks from videos can also be read
    def test_embedded_subtitles(self):
        s = Subtitles("resources/wSubs.mp4", track_index=0)

        self.assertEqual(s.track_index, 0)

        for i in range(len(SUBS)):
            s._get_next()
            self.assertEqual(s.start, SUBS[i][0])
            self.assertEqual(s.end, SUBS[i][1])
            self.assertEqual(s.text, SUBS[i][2])

    # tests choosing audio tracks
    def test_audio_track(self):
        for audio_handler in (True, False):
            v = Video(VIDEO_PATH, use_pygame_audio=audio_handler)
            self.assertEqual(v.audio_track, 0)
            v.set_audio_track(1)
            self.assertEqual(v.audio_track, 1)
            self.assertRaises(EOFError if not v.use_pygame_audio else pygame.error, timed_loop, 3, v.update)
            v.set_audio_track(0)
            while_loop(lambda: v.frame < 10, v.update, 10)
            self.assertEqual(v.audio_track, 0)
            v.set_audio_track(0)
            self.assertFalse(v._audio.loaded)
            v.close()

    # tests that videos properly restart
    def test_restart(self):
        v = Video(VIDEO_PATH)
        while_loop(lambda: v.frame < 10, v.update, 10)
        v.restart()
        self.assertEqual(v.frame, 0)
        self.assertEqual(v.get_pos(), 0)
        self.assertTrue(v.active)
        v.stop()
        v.restart()
        self.assertEqual(v.frame, 0)
        self.assertEqual(v.get_pos(), 0)
        self.assertTrue(v.active)
        v.close()

    # tests videos are properly resized
    def test_resize(self):
        v = Video(VIDEO_PATH)

        ORIGINAL_SIZE = v.original_size
        NEW_SIZE = (v.original_size[0] * 2, v.original_size[1] * 2)

        self.assertEqual(v.current_size, ORIGINAL_SIZE)
        v.resize(NEW_SIZE)
        self.assertEqual(v.current_size,NEW_SIZE)
        self.assertEqual(v.original_size, ORIGINAL_SIZE)

        # checks that the original aspect ratio was maintained
        v.resize((v.original_size[0], v.current_size[1]))
        self.assertNotEqual(v.aspect_ratio, (v.current_size[0] / v.current_size[1]))
        self.assertEqual(v.aspect_ratio, (v.original_size[0] / v.original_size[1]))

        # checks that read frames are indeed resized
        v.resize(NEW_SIZE)
        frame = next(v)
        self.assertEqual(frame.shape, (NEW_SIZE[1], NEW_SIZE[0], 3))

        # load a frame
        while_loop(lambda: v.frame_surf is None, v.update, 3)

        self.assertEqual(v.frame_surf.get_size(), NEW_SIZE)
        v.resize(ORIGINAL_SIZE)
        self.assertEqual(v.frame_surf.get_size(), ORIGINAL_SIZE)

        v.close()

    # tests that frame_surf and frame_data are working properly
    def test_frame_information(self):
        v = Video(VIDEO_PATH)

        self.assertEqual(v.frame, 0)
        self.assertIs(v.frame_surf, None)
        self.assertIs(v.frame_data, None)

        v.seek_frame(10)

        # frame information does not immediately update after seeking
        self.assertEqual(v.frame, 10)
        self.assertIs(v.frame_surf, None)
        self.assertIs(v.frame_data, None)

        # update frame information
        while_loop(lambda: not v.update(), lambda: None, 5)

        # check that frame information has been updated
        self.assertEqual(v.frame, 11)
        self.assertIsNot(v.frame_surf, None)
        self.assertIsNot(v.frame_data, None)

        # finish video
        v.seek(v.duration)
        while_loop(lambda: v.active, v.update, 5)

        # check that frame information has reset
        self.assertEqual(v.frame, 0)
        self.assertIs(v.frame_surf, None)
        self.assertIs(v.frame_data, None)

        v.close()

    # tests that the correct audio handlers are being selected
    def test_audio_handler(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(type(v._audio).__name__, "PyaudioHandler")

        # play a bit of audio and check that pyaudio is being utilized
        while_loop(lambda: v.frame < 10, v.update, 5)
        self.assertTrue(v._audio.thread is not None and v._audio.thread.is_alive())

        v.close()

        v = Video(VIDEO_PATH, use_pygame_audio=True)
        self.assertEqual(type(v._audio).__name__, "MixerHandler")

        # play a bit of audio and check that pygame is being utilized
        while_loop(lambda: v.frame < 10, v.update, 5)
        self.assertTrue(pygame.mixer.music.get_busy())

        v.close()

    # tests that different types of videos can be opened in reverse
    def test_reverse(self):
        for vfr in (True, False):
            v = Video(VIDEO_PATH, reverse=True, vfr=vfr)
            for i, frame in enumerate(v):
                self.assertTrue(check_same_frames(frame, v._preloaded_frames[v.frame_count - i - 1]))
            v.close()
        with open(VIDEO_PATH, "rb") as f:
            v = Video(f.read(), reverse=True)
            for i, frame in enumerate(v):
                self.assertTrue(check_same_frames(frame, v._preloaded_frames[v.frame_count - i - 1]))
            v.close()
        v = Video(YOUTUBE_PATH, reverse=True, youtube=True)
        for i, frame in enumerate(v):
            self.assertTrue(check_same_frames(frame, v._preloaded_frames[v.frame_count - i - 1]))
        v.close()

    # tests that youtube videos do not hang when close is called
    def test_hanging(self):
        v = Video(YOUTUBE_PATH, youtube=True, max_threads=10, max_chunks=10)
        t = time.time()
        v.close()
        self.assertLess(time.time() - t, 0.1)

    # test chunks_len method
    def test_chunks_length(self):
        v = self.static_video
        self.assertEqual(v._chunks_len([]), 0)  # No chunks
        self.assertEqual(v._chunks_len([None, None, None]), 0)  # All None
        self.assertEqual(v._chunks_len([1, None, 2, 3]), 3)  # Some None
        self.assertEqual(v._chunks_len([None, 5, None]), 1)  # Single non-None
        self.assertEqual(v._chunks_len([1, 2, 3]), 3)  # All non-None

    # tests that ffmpeg logs are hidden in case they were turned on and forgotten
    def test_ffmpeg_loglevel(self):
        self.assertEqual(FFMPEG_LOGLVL, "quiet")

    # test get_closest_frame method
    def test_get_closest_frame(self):
        v = self.static_video
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 4), 1)  # Closest to 4 is index 1 (3)
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 6), 2)  # Closest to 6 is index 2 (5)
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 7), 3)  # Exact match at index 3
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 8), 3)  # Closest to 8 is index 3 (7)
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 0), 0)  # Closest to 0 is index 0 (1)
        self.assertEqual(v._get_closest_frame([10, 20, 30], 25), 1)  # Closest to 25 is index 1 (20)
        self.assertEqual(v._get_closest_frame([10, 20, 30], 5), 0)  # Closest to 5 is index 0 (10)
        self.assertEqual(v._get_closest_frame([10, 20, 30], 35), 2)  # Closest to 35 is index 2 (30)

    # tests that an error is raised if missing ffmpeg
    def test_missing_ffmpeg(self):
        v = Video(VIDEO_PATH)
        v._missing_ffmpeg = True
        self.assertRaises(FileNotFoundError, v.update)
        v.close()

    # tests that volume is wokring properly
    def test_volume(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(v.volume, 1.0)
        self.assertEqual(v.get_volume(), 1.0)

        v.set_volume(0)
        self.assertEqual(v.volume, 0.0)
        v.set_volume(1.0)
        self.assertEqual(v.volume, 1.0)

        v.set_volume(0)
        self.assertEqual(v.volume, 0.0)
        v.set_volume(2)
        self.assertEqual(v.volume, 1.0)

        v.set_volume(0.5)

        self.assertEqual(pygame.mixer.music.get_volume() if v.use_pygame_audio else v._audio.get_volume(), v.volume)

        v.close()

    # test playing video in reverse and sped up
    def test_reversed_and_speed(self):
        v = Video(VIDEO_PATH, reverse=True, speed=3)
        seconds_elapsed = 0
        clock = pygame.time.Clock()
        v.play()
        timer = 0
        frames = 0
        avg_fps = 0
        while v.active:
            dt = clock.tick(0)
            timer += dt
            if timer >= 1000:
                seconds_elapsed += 1
                avg_fps += frames
                timer = 0
                frames = 0
            if v.update():
                frames += 1
                self.assertTrue(check_same_frames(v.frame_data, v._preloaded_frames[v.frame_count - v.frame]))
        # check that frame rate kept up
        self.assertGreaterEqual(avg_fps / v.duration, v.frame_rate * 0.7)
        v.close()

    # tests buffering is working properly
    def test_buffering(self):
        v = Video(VIDEO_PATH)
        self.assertFalse(v.buffering)
        v.update()
        self.assertTrue(v.buffering)
        while_loop(lambda: v.buffering, v.update, 5)
        self.assertFalse(v.buffering)
        self.assertTrue(v._audio.loaded)
        v.close()

    # test windows audio devices
    def test_audio_device(self):
        # test that an error is raised if opened using an input device
        index = find_device(lambda d: d["max_output_channels"] == 0)
        v = Video(VIDEO_PATH, audio_index=index, use_pygame_audio=False)
        self.assertEqual(v._audio.device_index, index)
        self.assertRaises(AudioDeviceError, while_loop, lambda: v.frame < 10, v.update, 10)
        self.assertRaises(AudioDeviceError, lambda: v._audio._set_device_index(9999999999999))
        v.close()

        # test video on different output devices
        for device in query_devices():
            if device["max_output_channels"] > 0 and device["hostapi"] == 0:
                index = device["index"]
                v = Video(VIDEO_PATH, audio_index=index)
                self.assertEqual(v._audio.device_index, index)
                while_loop(lambda: v.frame < 10, v.update, 3)
                v.close()

    # tests that each video can be opened in vfr mode
    def test_vfr(self):
         for file in PATHS:
             v = Video(file, vfr=True)
             self.assertGreater(len(v.timestamps), 0)
             self.assertTrue(v.vfr, f"{file} failed unit test")
             v.close()

    # tests seeking in vfr mode
    def test_vfr_seeking(self):
        v = Video(VIDEO_PATH, vfr=True)

        v.seek(-100, relative=False)
        self.assertEqual(v.frame, 0)
        self.assertEqual(v.get_pos(), 0.0)

        v.seek_frame(-50)
        self.assertEqual(v.frame, 0)
        self.assertEqual(v.get_pos(), v.timestamps[0])

        v.seek(v.duration, relative=False)
        self.assertEqual(v.get_pos(), v.duration)
        self.assertEqual(v.frame, v.frame_count - 1)

        # should never raise a stopIteration exception
        next(v)

        v.seek_frame(v.frame_count, relative=False)
        self.assertEqual(v.get_pos(), v.timestamps[-1])
        self.assertEqual(v.frame, v.frame_count - 1)

        for i in range(5):
            rand = random.uniform(0, v.duration)
            v.seek(rand, relative=False)
            self.assertEqual(v.get_pos(), rand)

            rand = random.randrange(0, v.frame_count)
            v.seek_frame(rand)
            self.assertEqual(v.frame, rand)
            self.assertEqual(v.get_pos(), v.timestamps[rand])

        v.close()

    # tests seeking for reversed videos
    def test_reverse_seek(self):
        v = Video(VIDEO_PATH, reverse=True)
        v.seek_frame(0)
        self.assertTrue(check_same_frames(next(v), v._preloaded_frames[-1]))
        v.seek_frame(v.frame_count - 1)
        self.assertTrue(check_same_frames(next(v), v._preloaded_frames[0]))
        v.close()

    # tests for errors for unsupported youtube links
    def test_bad_youtube_links(self):
        for url in ("https://www.youtube.com/@joewoobie1155", "https://www.youtube.com/channel/UCY3Rgenpuy4cY79eGk6DmuA", "https://www.youtube.com/", "https://www.youtube.com/shorts"):
            with self.assertRaises(YTDLPError):
                Video(url, youtube=True).close()
            time.sleep(0.1)

    # tests video in a context manager
    def test_context_manager(self):
        with Video(VIDEO_PATH) as v:
            self.assertFalse(v.closed)
        self.assertTrue(v.closed)

    # tests that when a video is preloaded, frames no longer need to be read on the fly
    def test_preloaded_playback(self):
        v = Video("resources\\clip.mp4")
        v._preload_frames()
        while_loop(lambda: v.frame < 50, lambda: (v.update(), self.assertEqual(v._vid._vidcap.get(cv2.CAP_PROP_POS_FRAMES), 0)), 3)
        v.close()

    # tests that an error is raised when bytes is empty
    def test_bad_bytes(self):
        with self.assertRaises(VideoStreamError) as context:
            Video(b'', as_bytes=True).close()
        self.assertEqual(str(context.exception), "Could not determine video.")

    # tests that an error is raised when there are no video tracks
    def test_no_video_tracks(self):
        with self.assertRaises(VideoStreamError) as context:
            Video("resources/nov.mp4").close()
        self.assertEqual(str(context.exception), "No video tracks found.")

    # tests the calculations of frame rate stats in vfr mode
    def test_variable_frame_rates(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(v.min_fr, v.max_fr)
        self.assertEqual(v.min_fr, v.avg_fr)
        v.close()
        v = Video(VIDEO_PATH, vfr=True)
        self.assertNotEqual(v.min_fr, v.max_fr)
        self.assertNotEqual(v.min_fr, v.avg_fr)
        self.assertEqual(round(v.min_fr, 2), 23.98)
        self.assertEqual(round(v.max_fr, 2), 23.98)
        self.assertEqual(round(v.avg_fr, 2), 23.98)
        self.assertEqual(v._get_vfrs([]), (0, 0, 0))
        v.close()

    # test that playing after frame-by-frame iteration is automatically seeked
    def test_frame_iteration(self):
        for audio_handler in (True, False):
            v = Video(VIDEO_PATH, use_pygame_audio=audio_handler)
            for i in range(50):
                next(v)
            v.play()
            while_loop(lambda: not v._audio.loaded, v.update, 5)
            self.assertEqual(round(v.get_pos()), 2)
            self.assertEqual(round(v._audio.get_pos()), 0)
            v.seek_frame(v.frame_count - 1)
            next(v)
            self.assertRaises(StopIteration, lambda: next(v))
            v.close()

    # tests that nothing crashes when selecting different languages with Youtube
    def test_youtube_language_tracks(self):
        for lang in (None, "en-US", "fr-FR", "es-US", "it", "pt-BR", "de-DE", "badcode"):
            v = Video("https://www.youtube.com/watch?v=v4H2fTgHGuc", youtube=True, pref_lang=lang)
            timed_loop(3, v.update)
            v.close()

    # tests force draw
    def test_draw(self):
        for force_draw in (False, True):
            v = Video(VIDEO_PATH)
            surf = pygame.Surface(v.original_size)
            clock = pygame.time.Clock()
            flag = True
            while v.active:
                clock.tick(60)

                # randomize surface
                surf.fill("blue")
                for i in range(5):
                    pygame.draw.circle(surf, "red", (random.randrange(0, v.original_size[0]), random.randrange(0, v.original_size[1])), random.randint(1, 5))
                array = pygame.surfarray.array3d(surf)

                drawn = v.draw(surf, (0, 0), force_draw=force_draw)

                # check that flickering is produced when force draw is off
                if v.frame_surf is not None:
                    if check_same_frames(pygame.surfarray.array3d(surf), array):
                        self.assertFalse(drawn)
                        flag = False
                        break
                    else:
                        self.assertTrue(drawn)

            v.close()
            self.assertEqual(flag, force_draw)

    # tests that previews start from where the video position is, and that they close the video afterwards
    def test_preview(self):
        v = Video(VIDEO_PATH)
        v.seek(v.duration)
        thread = Thread(target=lambda: v.preview())
        thread.start()
        time.sleep(1)
        self.assertFalse(thread.is_alive())
        self.assertTrue(v.closed)
        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, 1280, 720))
        v.seek(v.duration)
        thread = Thread(target=lambda: vp.preview())
        thread.start()
        time.sleep(1)
        self.assertFalse(thread.is_alive())
        self.assertTrue(vp.closed)

    # more of a visual test that tests minor misc features
    def test_additional_tests(self):
        s1 = Subtitles("resources\\subs1.srt", colour="blue", highlight="red", font=pygame.font.SysFont("arial", 35), offset=70, delay=-1)
        s2 = Subtitles("resources\\subs2.srt", colour=pygame.Color("pink"), highlight=(129, 12, 31, 128), font=pygame.font.SysFont("arial", 20))
        s3 = Subtitles("resources\\subs2.srt", colour=(123, 13, 52, 128), highlight=(4, 131, 141, 200), font=pygame.font.SysFont("arial", 40), delay=1)
        s4 = Subtitles("resources\\subs1.srt", delay=10000)
        font = pygame.font.SysFont("arial", 10)
        self.assertRaises(ValueError, lambda: s1.set_font(pygame.font.Font))
        s1.set_font(font)
        self.assertIs(font, s1.get_font())
        v = Video(VIDEO_PATH, subs=(s1, s2, s3, s4), speed=5)
        vp = VideoPlayer(v, (0, 0, 1280, 720), interactable=True, font_size=40)
        vp.close()

    # tests for a bug where the last frame would hang in situations like this
    def test_frame_bug(self):
        v = Video(VIDEO_PATH, speed=5)
        v.seek(65.19320347222221, False)
        thread = Thread(target=lambda: v.preview())
        thread.start()
        time.sleep(1)
        self.assertFalse(thread.is_alive())

    # tests different ways to accessing version
    def test_version(self):
        VER = "0.9.25"
        self.assertEqual(VER, VERSION)
        self.assertEqual(VER, pyvidplayer2._version.__version__)
        self.assertEqual(VER, get_version_info()["pyvidplayer2"])

    # tests opening subtitle files with different encodings
    def test_subtitle_encoding(self):
        self.assertRaises(SubtitleError, lambda: Subtitles("resources\\utf16.srt"))
        Subtitles("resources\\utf16.srt", encoding="utf16")

    # tests that the correct pts are extracted for vfr videos
    def test_get_timestamps(self):
        v = Video(VIDEO_PATH, vfr=True)
        self.assertEqual(v.timestamps[:10], [0.0, 0.041708, 0.083417, 0.125125, 0.166833, 0.208542, 0.25025, 0.291958,
                                        0.333667, 0.375375])
        self.assertEqual(v.timestamps[-10:], [66.858458, 66.900167,
                                        66.941875, 66.983583, 67.025292, 67.067, 67.108708, 67.150417, 67.192125,
                                        67.233833])
        v.close()

    # tests zoom out and zoom to fill
    def test_zoom(self):
        for i in range(100):
            pos = (random.randint(0, 2000), random.randint(0, 2000))
            size = (random.randint(100, 2000), random.randint(100, 2000))
            vp = VideoPlayer(self.static_video, (*pos, *size))

            original_vid_rect = vp.vid_rect.copy()
            original_frame_rect = vp.frame_rect.copy()

            self.assertTrue(vp.vid_rect.w == vp.frame_rect.w or vp.vid_rect.h == vp.frame_rect.h)
            self.assertEqual(vp.vid_rect.center, vp.frame_rect.center)
            self.assertFalse(vp._zoomed)
            vp.zoom_to_fill()
            self.assertGreaterEqual(vp.vid_rect.w, vp.frame_rect.w)
            self.assertGreaterEqual(vp.vid_rect.h, vp.frame_rect.h)
            self.assertEqual(vp.vid_rect.center, vp.frame_rect.center)
            self.assertTrue(vp._zoomed)
            vp.toggle_zoom()
            self.assertFalse(vp._zoomed)
            vp.toggle_zoom()
            self.assertTrue(vp._zoomed)
            vp.zoom_to_fill()
            vp.zoom_out()
            vp.zoom_out()

            self.assertEqual(vp.vid_rect, original_vid_rect)
            self.assertEqual(vp.frame_rect, original_frame_rect)

    # tests default video player
    def test_open_video_player(self):
        vp = VideoPlayer(self.static_video, (0, 0, *self.static_video.original_size))
        self.assertIs(vp.video, self.static_video)
        self.assertIs(vp.get_video(), self.static_video)
        self.assertEqual(vp.vid_rect, pygame.Rect(0, 0, self.static_video.original_size[0], self.static_video.original_size[1]))
        self.assertEqual(vp.frame_rect, pygame.Rect(0, 0, self.static_video.original_size[0], self.static_video.original_size[1]))
        self.assertFalse(vp.interactable)
        self.assertFalse(vp.loop)
        self.assertEqual(vp.preview_thumbnails, 0)
        self.assertEqual(vp._font.point_size, 10)
        self.assertEqual(vp._font.name, "Arial")

    # tests queue system
    def test_queue(self):
        original_video = Video("resources\\clip.mp4")

        vp = VideoPlayer(original_video, (0, 0, *original_video.original_size))
        self.assertEqual(len(vp.queue_), 0)
        self.assertIs(vp.get_queue(), vp.queue_)

        self.assertIs(vp.get_next(), None)

        v1 = Video("resources\\trailer1.mp4")
        v2 = Video("resources\\ocean.mkv")
        v3 = Video("resources\\medic.mov")
        v4 = Video("resources\\birds.avi")

        # v1 is not loaded when it is created
        self.assertTrue(v1.active)
        self.assertEqual(len(v1._chunks), 0)

        vp.queue(v1)

        # v1 is now loading after queueing happens
        self.assertFalse(v1.active)
        self.assertEqual(len(v1._chunks), 1)
        self.assertEqual(v1._chunks_len(v1._chunks), 0)

        vp.queue(v2)
        vp.queue(v3)
        vp.queue(v4)

        self.assertEqual(len(vp.queue_), 4)
        self.assertEqual(len(vp), 5)

        self.assertIs(vp.get_next(), v1)

        # play first clip in its entirety
        timed_loop(8, vp.update)

        self.assertIs(vp.video, v1)
        self.assertEqual(len(vp.queue_), 3)
        self.assertEqual(len(vp), 4)
        self.assertTrue(original_video.closed)

        vp.skip()

        self.assertIs(vp.video, v2)
        self.assertEqual(len(vp.queue_), 2)
        self.assertTrue(v1.closed)

        vp.skip() # should be on v3 after skip
        vp.skip() # should be on v4 after skip

        self.assertIs(vp.video, v4)
        self.assertEqual(len(vp), 1)
        self.assertIs(vp.get_next(), None)

        # shouldn't do anything
        for i in range(10):
            vp.skip()

        self.assertTrue(v4.active)

        vp.close()
        self.assertTrue(vp.video.closed)
        self.assertEqual(len(vp), 1)
        self.assertEqual(len(vp.queue_), 0)
        for v in (v1, v2, v3, v4):
            self.assertTrue(v.closed)

    # tests queue system with loop
    def test_queue_loop(self):
        original_video = Video("resources\\trailer1.mp4")
        v1 = Video("resources\\trailer2.mp4")
        v2 = Video("resources\\clip.mp4")

        vp = VideoPlayer(original_video, (0, 0, *original_video.original_size), loop=True)
        vp.queue(v1)
        vp.queue(v2)

        vp.skip()
        vp.skip()

        self.assertIs(vp.get_video(), v2)
        self.assertFalse(v1.active)
        self.assertFalse(original_video.active)
        self.assertEqual(vp.queue_, [original_video, v1])

        # play first clip in its entirety
        timed_loop(8, vp.update)

        self.assertIs(vp.video, original_video)
        self.assertEqual(len(vp.queue_), 2)
        self.assertEqual(len(vp), 3)

        # queue an incorrect argument
        vp.queue(1)

        # manually wipe queue
        vp.clear_queue()
        for v in (v1, v2):
            self.assertTrue(v.closed)
        self.assertEqual(len(vp.queue_), 0)

        original_video.stop()
        vp.update() # should trigger _handle_on_end
        self.assertEqual(original_video.get_pos(), 0.0)
        self.assertTrue(original_video.active)

        vp.close()

    # tests the move method video player
    def test_move_video_player(self):
        vp = VideoPlayer(self.static_video, (0, 0, *self.static_video.original_size))

        vid_pos = vp.vid_rect.topleft
        vid_size = vp.vid_rect.size

        vp.move((10, 10))
        self.assertEqual(vp.frame_rect.topleft, (10, 10))

        # ensure default setting is not relative
        vp.move((10, 10))
        self.assertEqual(vp.frame_rect.topleft, (10, 10))

        vp.move((10, 10), relative=True)
        self.assertEqual(vp.frame_rect.topleft, (20, 20))

        # ensures that vid rect was properly changed
        self.assertNotEqual(vp.vid_rect.topleft, vid_pos)
        self.assertEqual(vp.vid_rect.size, vid_size)

    # tests queueing with video paths instead of objects
    def test_queue_str_path(self):
        original_video = Video(VIDEO_PATH)
        vp = VideoPlayer(original_video, (0, 0, *original_video.original_size), loop=True)

        vp.queue("resources\\trailer2.mp4")
        vp.queue("resources\\clip.mp4")

        self.assertEqual(vp.queue_, ["resources\\trailer2.mp4", "resources\\clip.mp4"])

        vp.skip()
        vp.skip()

        self.assertEqual(vp.queue_[0].name, "trailer1")
        self.assertEqual(vp.queue_[1].name, "trailer2")

        vp.clear_queue()
        vp.queue("badpath")
        self.assertRaises(FileNotFoundError, vp.skip)
        vp.close()

    # tests that each preview thumbnail is read
    def test_preview_thumbnails(self):
        original_video = Video("resources\\clip.mp4")

        # test that preview thumbnail loading does not change vid frame pointer
        self.assertEqual(original_video._vid._vidcap.get(cv2.CAP_PROP_POS_FRAMES), 0)
        vp = VideoPlayer(original_video, (0, 0, *original_video.original_size), preview_thumbnails=30)
        self.assertEqual(original_video._vid._vidcap.get(cv2.CAP_PROP_POS_FRAMES), 0)

        self.assertEqual(len(vp._interval_frames), 31)
        self.assertEqual(vp.video._vid.frame, 0)

        viewed_thumbnails = []
        for i in range(int(original_video.duration * 10)):
            thumbnail = vp._get_closest_frame(i * 0.1)
            if not thumbnail in viewed_thumbnails:
                viewed_thumbnails.append(thumbnail)

        # ensures that when preloaded, the preview thumbnails are taken straight from the preloaded frames
        original_video._preload_frames()
        t = Thread(target=lambda: VideoPlayer(original_video, (0, 0, *original_video.original_size), preview_thumbnails=300))
        t.start()
        time.sleep(10)
        self.assertFalse(t.is_alive())

        # checks that loaded preview thumbnails from both methods produce the same frames
        vp2 = VideoPlayer(original_video, (0, 0, *original_video.original_size), preview_thumbnails=30)
        for f1, f2 in zip(vp._interval_frames, vp2._interval_frames):
            self.assertTrue(check_same_frames(pygame.surfarray.array3d(f1), pygame.surfarray.array3d(f2)))

        self.assertEqual(original_video._vid._vidcap.get(cv2.CAP_PROP_POS_FRAMES), 0)

    # tests the _best_fit method for videoplayer
    def test_best_fit(self):
        vp = self.static_player

        # Test case 1: Rectangle with exact aspect ratio
        rect = pygame.Rect(0, 0, 1920, 1080)
        aspect_ratio = 16 / 9
        expected = pygame.Rect(0, 0, 1920, 1080)
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 2: Width limiting, maintaining aspect ratio
        rect = pygame.Rect(0, 0, 1920, 1080)
        aspect_ratio = 4 / 3
        expected = pygame.Rect(240, 0, 1440, 1080)  # Centered horizontally
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 3: Height limiting, maintaining aspect ratio
        rect = pygame.Rect(0, 0, 1080, 1920)
        aspect_ratio = 16 / 9
        expected = pygame.Rect(0, 656, 1080, 607)  # Centered vertically
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 4: Square rectangle with wide aspect ratio
        rect = pygame.Rect(0, 0, 1000, 1000)
        aspect_ratio = 16 / 9
        expected = pygame.Rect(0, 219, 1000, 562)  # Centered vertically
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 5: Square rectangle with tall aspect ratio
        rect = pygame.Rect(0, 0, 1000, 1000)
        aspect_ratio = 9 / 16
        expected = pygame.Rect(219, 0, 562, 1000)  # Centered horizontally
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 6: Rectangle fully inside another with the same aspect ratio
        rect = pygame.Rect(100, 100, 1920, 1080)
        aspect_ratio = 16 / 9
        expected = pygame.Rect(100, 100, 1920, 1080)
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 7: Aspect ratio = 1 (square fit)
        rect = pygame.Rect(0, 0, 1920, 1080)
        aspect_ratio = 1
        expected = pygame.Rect(420, 0, 1080, 1080)  # Fit to height
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 8: Extremely wide aspect ratio
        rect = pygame.Rect(0, 0, 1920, 1080)
        aspect_ratio = 32 / 9
        expected = pygame.Rect(0, 270, 1920, 540)  # Fit to width, centered vertically
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 9: Extremely tall aspect ratio
        rect = pygame.Rect(0, 0, 1920, 1080)
        aspect_ratio = 9 / 32
        expected = pygame.Rect(808, 0, 303, 1080)  # Fit to height, centered horizontally
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

        # Test case 10: Zero-size rectangle (edge case)
        rect = pygame.Rect(0, 0, 0, 0)
        aspect_ratio = 16 / 9
        expected = pygame.Rect(0, 0, 0, 0)  # No space to fit
        self.assertEqual(vp._best_fit(rect, aspect_ratio), expected)

    # tests _convert_seconds for videoplayer
    def test_video_player_convert_seconds(self):
        vp = self.static_player

        # Whole Hours
        self.assertEqual(vp._convert_seconds(3600), "1:0:0")
        self.assertEqual(vp._convert_seconds(7200), "2:0:0")

        # Hours and Minutes
        self.assertEqual(vp._convert_seconds(3660), "1:1:0")
        self.assertEqual(vp._convert_seconds(7325), "2:2:5")

        # Minutes and Seconds
        self.assertEqual(vp._convert_seconds(65), "0:1:5")
        self.assertEqual(vp._convert_seconds(125), "0:2:5")

        # Seconds Only
        self.assertEqual(vp._convert_seconds(5), "0:0:5")
        self.assertEqual(vp._convert_seconds(59), "0:0:59")

        # Fractional Seconds
        self.assertEqual(vp._convert_seconds(5.3), "0:0:5")
        self.assertEqual(vp._convert_seconds(125.6), "0:2:5")
        self.assertEqual(vp._convert_seconds(7325.9), "2:2:5")

        # Zero Seconds
        self.assertEqual(vp._convert_seconds(0), "0:0:0")

        # Large Number
        self.assertEqual(vp._convert_seconds(86400), "24:0:0")
        self.assertEqual(vp._convert_seconds(90061.5), "25:1:1")

        # Negative Seconds
        self.assertEqual(vp._convert_seconds(-5), "0:0:5")
        self.assertEqual(vp._convert_seconds(-3665), "1:1:5")

    # tests different arguments for videoplayers to check for errors
    def test_bad_player_path(self):
        with self.assertRaises(ValueError) as context:
            VideoPlayer("badpath", (0, 0, 100, 100))

        with self.assertRaises(ValueError) as context:
            VideoPlayer(VideoTkinter(VIDEO_PATH), (0, 0, 100, 100))

        v = Video(VIDEO_PATH)
        v.close()
        with self.assertRaises(VideoStreamError) as context:
            VideoPlayer(v, (0, 0, *v.original_size))
        self.assertEqual(str(context.exception), "Provided video is closed.")

    # tests default webcam
    def test_open_webcam(self):
        w = Webcam()
        self.assertNotEqual(w.original_size, (0, 0))
        self.assertEqual(w.original_size, w.current_size)
        self.assertEqual(w.aspect_ratio, (w.original_size[0] / w.original_size[1]))
        self.assertIs(w.frame_data, None)
        self.assertIs(w.frame_surf, None)
        self.assertFalse(w.closed)
        self.assertTrue(w.active)
        self.assertIs(w.post_func, PostProcessing.none)
        self.assertEqual(w.interp, cv2.INTER_LINEAR)
        self.assertEqual(w.fps, 30)
        self.assertEqual(w.cam_id, 0)
        w.close()

    # tests that webcam plays without errors
    def test_webcam_playback(self):
        w = Webcam()
        timed_loop(5, lambda: (w.update(), self.assertIsNot(w.frame_surf, None)))
        w.close()

    # tests webcam resizing features
    def test_webcam_resize(self):
        w = Webcam(capture_size=(640, 480))
        self.assertEqual(w.original_size, (640, 480))
        self.assertEqual(w.original_size[0], w._vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.assertEqual(w.original_size[1], w._vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        w.resize((1280, 720))
        self.assertEqual(w.original_size, (640, 480))
        self.assertEqual(w.current_size, (1280, 720))
        w.update()  # captures a frame
        self.assertEqual(w.frame_data.shape, (720, 1280, 3))
        w.resize((1920, 1080))
        self.assertEqual(w.original_size, (640, 480))
        self.assertEqual(w.current_size, (1920, 1080))
        self.assertEqual(w.frame_data.shape, (1080, 1920, 3))
        w.change_resolution(480)
        self.assertEqual(w.original_size, (640, 480))
        self.assertEqual(w.current_size, (640, 480))
        self.assertEqual(w.frame_data.shape, (480, 640, 3))
        w.close()

    # tests webcam position accuracy
    # right now is not very accurate, will improve soon
    def test_webcam_get_pos(self):
        w = Webcam()
        t = time.time()
        while time.time() - t < 10:
            w.update()
        self.assertTrue(w.get_pos() > 9)

    # tests that webcam plays and stops properly
    def test_webcam_active(self):
        w = Webcam()
        self.assertTrue(w.active)
        w.play()
        self.assertTrue(w.active)
        w.stop()
        self.assertFalse(w.active)
        w.stop()
        self.assertFalse(w.active)
        w.play()
        self.assertTrue(w.active)
        w.close()
        self.assertTrue(w.closed)

    # tests that webcam can achieve 60 fps
    # fails on webcams under 60 fps
    def test_webcam_60_fps(self):
        w = Webcam(fps=30)
        t = time.time()
        while time.time() - t < 10:
            w.update()
        self.assertTrue(w._frames / 30 > 8)
        w = Webcam(fps=60)
        t = time.time()
        while time.time() - t < 10:
            w.update()
        self.assertTrue(w._frames / 60 > 8)


if __name__ == "__main__":
    unittest.main()
