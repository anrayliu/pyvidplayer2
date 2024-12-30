import math
import random
import unittest
from copy import deepcopy
import numpy as np
import pygame
import os
import time
import cv2
from pyvidplayer2 import *


def get_videos():
    paths = []
    for file in os.listdir("resources"):
        for ext in ("mp4", "avi", "webm", "mov", "mkv"):
            if file.endswith(ext):
                paths.append(os.path.join("resources", file))
    return paths

def check_same_frames(f1, f2):
    diff = cv2.subtract(f1, f2)
    b, g, r = cv2.split(diff)
    return cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0

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
    import yt_dlp

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info("https://www.youtube.com/feed/trending", download=False)

    if "entries" in info:
        return [entry["url"] for entry in info["entries"][:max_results]]
    else:
        raise RuntimeError("Could not extract youtube urls.")


PATHS = get_videos()
VIDEO_PATH = "resources\\trailer1.mp4"
YOUTUBE_PATH = "https://www.youtube.com/watch?v=K8PoK3533es&t=3s"

# test default state?


class TestVideo(unittest.TestCase):
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
        timed_loop(5, lambda: (v1.update(), v2.update()))

        # check for number of stored chunks
        self.assertEqual(len(v1._chunks), 1)
        self.assertEqual(len(v2._chunks), 5)

        v1.close()
        v2.close()

    def test_post_processing(self):
        # must be done with clip.mp4 because trailer1.mp4 fails letterbox due to it already having one
        # and trailer2.mp4 fails noise due to the black opening frames

        v1 = Video("resources\\clip.mp4")
        original_frame = next(v1)
        v2 = Video("resources\\clip.mp4")
        new_frame = next(v2)
        self.assertTrue(check_same_frames(original_frame, new_frame))

        for func in (lambda d: np.fliplr(d), PostProcessing.blur, PostProcessing.sharpen, PostProcessing.greyscale, PostProcessing.noise, PostProcessing.letterbox, PostProcessing.cel_shading):
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
        v.close()

        v = Video("https://www.youtube.com/watch?v=K8PoK3533es", youtube=True)
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
        v.close()

        with open("resources\\trailer1.mp4", "rb") as file:
            v = Video(file.read())
        self.assertTrue(type(v.path) == bytes)
        self.assertEqual(v._audio_path, "-")
        self.assertEqual(v.name, "")
        self.assertEqual(v.ext, "")
        self.assertEqual(v.duration, 67.27554166666665)
        self.assertEqual(v.frame_count, 1613)
        self.assertEqual(v.frame_rate, 23.976023976023978)
        self.assertEqual(v.original_size, (1280, 720))
        self.assertEqual(v.current_size, (1280, 720))
        self.assertEqual(v.aspect_ratio, 1.7777777777777777)
        v.close()

    def test_setting_interp(self):
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

        v.close()

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
            v.probe()

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
            self.assertEqual(v.get_pos(), round(FRAME / v.frame_rate, 2))
            self.assertEqual(v.frame, FRAME)

            new_frame = next(v)

            self.assertTrue(check_same_frames(original_frame, new_frame))

            # testing relative frame seek
            v.seek_frame(-FRAME, relative=True)
            self.assertEqual(v.get_pos(), round(1 / v.frame_rate, 2))
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

            self.assertEqual(v.get_pos(), math.floor(v.duration * 100) / 100.0)
            self.assertEqual(v.frame, v.frame_count - 1)

            v.seek_frame(v.frame_count)

            # should never raise a stop iteration exception
            new_frame = next(v)
            v.seek_frame(v.frame_count)

            self.assertEqual(v.get_pos(), round((v.frame_count - 1) / v.frame_rate, 2))
            self.assertEqual(v.frame, v.frame_count - 1)

            self.assertTrue(check_same_frames(original_frame, new_frame))

            # tests that when seeking to x, exactly x will be obtained when checking-
            for i in range(5):
                rand_time = math.floor(random.uniform(0, v.duration) * 100) / 100.0
                v.seek(rand_time, relative=False)
                self.assertEqual(v.get_pos(), rand_time)

                rand_frame = random.randrange(0, v.frame_count)
                v.seek_frame(rand_frame, relative=False)
                self.assertEqual(v.frame, rand_frame)

            v.close()

    def test_mm_len(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(v.frame_count, len(v))
        v.close()

    def test_init_subs(self):
        v = Video("resources\\trailer1.mp4")
        self.assertEqual(v.subs, [])
        v.close()

        s = Subtitles("resources\\subs1.srt")
        v = Video("resources\\trailer1.mp4", subs=s)
        self.assertEqual(v.subs, [s])
        v.close()

        v = Video("resources\\trailer1.mp4", subs=[s, s, s])
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

    def test_stop(self):
        v = Video(VIDEO_PATH)
        while_loop(lambda: v.frame < 10, v.update, 10)
        v.stop()
        self.assertFalse(v.active)
        self.assertEqual(v.frame_data, None)
        self.assertEqual(v.frame_surf, None)
        self.assertFalse(v.paused)
        v.stop() # test for exception
        v.close()

    def test_set_speed_method(self):
        v = Video(VIDEO_PATH)
        self.assertRaises(DeprecationWarning, v.set_speed, 1.0)

    def test_preloaded_frames(self):
        v = Video(VIDEO_PATH)
        v._preload_frames()
        for i, frame in enumerate(v):
            self.assertTrue(check_same_frames(v._preloaded_frames[i], frame))
        v.close()

    def test_frame_counts(self):
        for file in PATHS:
            v = Video(file)
            # check that header information was not completely wrong
            self.assertGreater(v.frame_count, 0)
            self.assertGreater(v.frame_rate, 0)
            self.assertGreater(v.duration, 0)

            v.probe()
            real = v._get_real_frame_count()
            self.assertEqual(v.frame_count, real, f"{file} failed unit test")
            self.assertGreater(v.frame_rate, 0)
            self.assertGreater(v.duration, 0)

            v.close()

    def test_convert_seconds(self):
        v = Video(VIDEO_PATH)

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

        v.close()

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

    def test_youtube(self):
        for url in get_youtube_urls():
            v = Video(url, youtube=True)
            self.assertTrue(v._audio_path.startswith("https"))
            self.assertTrue(v.path.startswith("https"))
            while_loop(lambda: v.get_pos() < 3, v.update, 10)
            v.close()

    def test_youtube_settings(self):
        v = Video(YOUTUBE_PATH, youtube=True, chunk_size=30, max_threads=3, max_chunks=3)
        self.assertEqual(v.chunk_size, 60)
        self.assertEqual(v.max_threads, 1)
        self.assertEqual(v.max_chunks, 3)
        v.close()

    def test_change_resolution(self):
        v = Video(VIDEO_PATH)
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
        v.close()

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

    def test_max_resolution(self):
        for res in (144, 360, 720, 1080):
            v = Video(YOUTUBE_PATH, youtube=True, max_res=res)
            self.assertEqual(v.current_size[1], res)
            v.close()
            time.sleep(0.1) # prevents spamming youtube

    # tests that most of the frame rate
    def test_unlocked_fps(self):
        for file in PATHS:
            v = Video(file)
            seconds_elapsed = 0
            avg_fps = 0
            clock = pygame.time.Clock()
            v.play()
            timer = 0
            frames = 0
            while v.active and seconds_elapsed < 10:
                dt = clock.tick(180)
                timer += dt
                if timer >= 1000:
                    seconds_elapsed += 1
                    avg_fps += frames
                    timer = 0
                    frames = 0
                if v.update():
                    frames += 1
            self.assertTrue((avg_fps / float(seconds_elapsed)) / v.frame_rate > 0.9, f"{file} failed unit test")
            v.close()

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
            timed_loop(5, v.update)
            self.assertEqual(frame, v.frame)

            v.toggle_pause()
            self.assertFalse(v.paused)
            v.toggle_pause()
            self.assertTrue(v.paused)

            v.close()

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

    def test_no_audio_detection(self):
        for file in PATHS:
            v = Video(file)
            self.assertEqual(v.no_audio, v.name in ("60fps", "silent", "hdr"), f"{file} failed unit test")
            v.close()

    def test_resampling(self):
        v = Video(VIDEO_PATH)
        original_frame = next(v)

        # ensures both resamplers are active
        cv_resampled = v._resize_frame(original_frame, (v.original_size[0] // 2, v.original_size[1] // 2), cv2.INTER_CUBIC, False)
        ffmpeg_resampled = v._resize_frame(original_frame, (v.original_size[0] // 2, v.original_size[1] // 2), "bicubic", True)
        self.assertFalse(check_same_frames(cv_resampled, ffmpeg_resampled))

        SIZES = ((426, 240), (640, 360), (854, 480), (1280, 720), (1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320))

        # test cv resamplers
        for size in SIZES:
            for flag in (cv2.INTER_LINEAR, cv2.INTER_NEAREST, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4, cv2.INTER_AREA):
                new_frame = v._resize_frame(original_frame, size, flag, False)
                self.assertEqual(new_frame.shape, (size[1], size[0], 3))
                if size == v.original_size:
                    self.assertTrue(check_same_frames(original_frame, new_frame))

        # test ffmpeg resamplers
        for size in SIZES:
            for flag in ("bilinear", "bicubic", "neighbor", "area", "lanczos"):
                new_frame = v._resize_frame(original_frame, size, flag, True)
                self.assertEqual(new_frame.shape, (size[1], size[0], 3))
                if size == v.original_size:
                    self.assertTrue(check_same_frames(original_frame, new_frame))

        v.close()

    # tests that subtitles are properly read and displayed
    def test_subtitles(self):
        v = Video("resources\\trailer1.mp4", subs=Subtitles("resources\\subs1.srt"), speed=5)
        v._preload_frames()

        LOADED_FRAMES = deepcopy(v._preloaded_frames)

        SUBS = [
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
        ]

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
                    self.assertFalse(
                        (pygame.surfarray.array3d(v.frame_surf) == pygame.surfarray.array3d(v._create_frame(
                            LOADED_FRAMES[v.frame - 1]))).all())
            if not in_interval:
                self.assertTrue(
                    (pygame.surfarray.array3d(v.frame_surf) == pygame.surfarray.array3d(v._create_frame(
                        LOADED_FRAMES[v.frame - 1]))).all())

        # test regular playback with subtitles
        while_loop(lambda: v.active, check_subs, 100)

        v.close()

    def test_audio_track(self):
        for audio_handler in (True, False):
            v = Video(VIDEO_PATH, use_pygame_audio=audio_handler)
            self.assertEqual(v.audio_track, 0)
            v.set_audio_track(1)
            self.assertEqual(v.audio_track, 1)
            self.assertRaises(EOFError if not v.use_pygame_audio else pygame.error, timed_loop, 5, v.update)
            v.set_audio_track(0)
            while_loop(lambda: v.frame < 10, v.update, 10)
            self.assertEqual(v.audio_track, 0)
            v.set_audio_track(0)
            self.assertFalse(v._audio.loaded)
            v.close()

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

        v.close()


# incorporate next in update
# internal subs



if __name__ == "__main__":
    unittest.main()
