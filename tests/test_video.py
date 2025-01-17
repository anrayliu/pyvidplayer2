import sys
import time
import unittest
import unittest.mock
import os
import random
from threading import Thread
import numpy as np
from sounddevice import query_devices
import pyvidplayer2
from pyvidplayer2 import *


def find_device(*lambdas):
    for device in query_devices():
        passed = True
        for func in lambdas:
            if not func(device):
                passed = False
        if passed:
            return device["index"]

    raise RuntimeError("Could not find specified sound device.")

def get_videos():
    paths = []
    for file in os.listdir("resources"):
        for ext in ("mp4", "avi", "webm", "mov", "mkv"):
            if file.endswith(ext) and not file.endswith("nov.mp4"): # causes a lot of issues with tests
                paths.append(os.path.join("resources", file))
    return paths

def timed_loop(seconds, func, dt=0.1):
    t = time.time() + seconds
    while time.time() < t:
        time.sleep(dt)
        func()

def while_loop(condition_func, func, timeout, dt=0.1):
    t = time.time()
    while condition_func():
        time.sleep(dt)
        func()
        if time.time() - t > timeout:
            raise RuntimeError("Loop timed out.")

def check_same_frames(f1, f2):
    return np.array_equal(f1, f2)


PATHS = get_videos()
VIDEO_PATH = "resources\\trailer1.mp4"


class TestVideo(unittest.TestCase):
    # tests each post processing function
    def test_post_processing(self):
        # must be done with clip.mp4 because trailer1.mp4 fails letterbox due to it already having one
        # and trailer2.mp4 fails noise due to the black opening frames

        v1 = Video("resources\\clip.mp4")
        original_frame = next(v1)
        v2 = Video("resources\\clip.mp4")
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
        self.assertEqual(type(v._vid).__name__, "DecordReader")
        v.close()

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

        v.close()

    # tests that each file can be opened and recognized as bytes
    # currently fails due to a bug
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

    # test __str__
    def test_str_magic_method(self):
        videos = {
                    "<VideoPygame(path=resources\\trailer1.mp4)>": Video(VIDEO_PATH),
                    "<VideoTkinter(path=resources\\trailer1.mp4)>": VideoTkinter(VIDEO_PATH),
                    "<VideoPyglet(path=resources\\trailer1.mp4)>": VideoPyglet(VIDEO_PATH),
                    "<VideoPyQT(path=resources\\trailer1.mp4)>": VideoPyQT(VIDEO_PATH),
                    "<VideoRaylib(path=resources\\trailer1.mp4)>": VideoRaylib(VIDEO_PATH),
                    "<VideoPySide(path=resources\\trailer1.mp4)>": VideoPySide(VIDEO_PATH)
                }

        for name, v in videos.items():
            self.assertEqual(name, str(v))
            v.close()

    # test if subs are initialized correctly
    def test_init_subs(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(v.subs, [])
        v.close()

        s = Subtitles("resources\\subs1.srt")
        v = Video(VIDEO_PATH, subs=s)
        self.assertEqual(v.subs, [s])
        v.close()

        v = Video(VIDEO_PATH, subs=[s, s, s])
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
        with Video(VIDEO_PATH) as v:
            self.assertRaises(DeprecationWarning, v.set_speed, 1.0)

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
    # currently fails due to a bug
    def test_frame_counts(self):
        for file in PATHS:
            v = Video(file)
            if v.name in ("av1",):
                continue # file is corrupt

            # check that header information was not completely wrong
            self.assertGreater(v.frame_count, 0)
            self.assertGreater(v.frame_rate, 0)
            self.assertGreater(v.duration, 0)

            self.assertEqual(v.frame_count, len(v))

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

        self.assertEqual(v._convert_seconds(4.98), "0:0:4.98")
        self.assertEqual(v._convert_seconds(4.98881), "0:0:4.98881")
        self.assertEqual(v._convert_seconds(12.1280937198881), "0:0:12.1280937198881")

        v.close()

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

    # test common resolutions
    def test_change_resolution(self):
        v = Video(VIDEO_PATH)

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

        v.close()

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

    # test each readers ability to choose the first video track when there are many
    # fails because decord does not read the first track
    def test_many_video_tracks(self):
        v = Video("resources\\birds.avi")
        vids = [Video("resources\\manyv.mp4", reader=reader) for reader in (READER_OPENCV, READER_FFMPEG, READER_IMAGEIO, READER_DECORD)]
        for i in range(10):
            frame = next(v)
            for vid in vids:
                self.assertTrue(check_same_frames(frame, next(vid)))
        v.close()
        [vid.close() for vid in vids]

    # test each reader's ability to handle 16 bit colours
    def test_16_bit_colour(self):
        for reader in (READER_OPENCV, READER_FFMPEG, READER_IMAGEIO, READER_DECORD):
            v = Video("resources\\16bit.mp4", reader=reader)
            while_loop(lambda: v.frame_surf is None, v.update, 5)
            v.close()

    # test each reader's ability to handle a single colour channel
    def test_grayscale(self):
        for reader in (READER_OPENCV, READER_FFMPEG, READER_IMAGEIO, READER_DECORD):
            v = Video("resources\\1channel.mp4", reader=reader)
            while_loop(lambda: v.frame_surf is None, v.update, 5)
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
            self.assertEqual(v.no_audio, v.name in ("60fps", "hdr", "test", "av1", "16bit", "1channel", "5frames"), f"{file} failed unit test")
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
    # test chunks_len method
    def test_chunks_length(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(v._chunks_len([]), 0)  # No chunks
        self.assertEqual(v._chunks_len([None, None, None]), 0)  # All None
        self.assertEqual(v._chunks_len([1, None, 2, 3]), 3)  # Some None
        self.assertEqual(v._chunks_len([None, 5, None]), 1)  # Single non-None
        self.assertEqual(v._chunks_len([1, 2, 3]), 3)  # All non-None
        v.close()

    # tests that ffmpeg logs are hidden in case they were turned on and forgotten
    def test_loglevels(self):
        self.assertEqual(FFMPEG_LOGLVL, "quiet")

    # test get_closest_frame method
    def test_get_closest_frame(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 4), 1)  # Closest to 4 is index 1 (3)
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 6), 2)  # Closest to 6 is index 2 (5)
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 7), 3)  # Exact match at index 3
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 8), 3)  # Closest to 8 is index 3 (7)
        self.assertEqual(v._get_closest_frame([1, 3, 5, 7], 0), 0)  # Closest to 0 is index 0 (1)
        self.assertEqual(v._get_closest_frame([10, 20, 30], 25), 1)  # Closest to 25 is index 1 (20)
        self.assertEqual(v._get_closest_frame([10, 20, 30], 5), 0)  # Closest to 5 is index 0 (10)
        self.assertEqual(v._get_closest_frame([10, 20, 30], 35), 2)  # Closest to 35 is index 2 (30)
        v.close()

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
    def test_open_vfr(self):
         for file in PATHS:
             v = Video(file, vfr=True)
             self.assertGreater(len(v.timestamps), 0)
             self.assertTrue(v.vfr, f"{file} failed unit test")
             v.close()

    # tests that frames appear at the correct timestamps for vfr videos
    def test_vfr(self):
        v = Video("resources\\vfr.mp4", vfr=True)
        v._preload_frames()
        def update():
            n = v.update()
            timestamp = v._update_time
            if v.frame != 0:
                if n:
                    self.assertTrue(check_same_frames(v._preloaded_frames[v.frame - 1], v.frame_data))
                    # tests that the timestamp for the current frame has passed
                    self.assertTrue(timestamp >= v.timestamps[v.frame - 1])
                else:
                    # tests that the timestamp for the next frame has not yet been reached
                    if v.frame == len(v._preloaded_frames):
                        self.assertTrue(timestamp < v.duration)
                    else:
                        self.assertTrue(timestamp < v.timestamps[v.frame])
        while_loop(lambda: v.active, update, 30)
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
        for reader in (READER_IMAGEIO, READER_DECORD):
            with self.assertRaises(VideoStreamError) as context:
                Video(b'', as_bytes=True, reader=reader).close()
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
    def test_previews(self):
        for lib in (Video, VideoTkinter, VideoPyglet, VideoRaylib, VideoPyQT, VideoPySide):
            v = lib(VIDEO_PATH)
            v.seek(v.duration)
            v.preview()
            self.assertTrue(v.closed)

    # tests that the last frame can be achieved
    # performs test by counting rendered frames
    def test_last_frame(self):
        PATH = "resources\\5frames.mp4"
        for v in (Video(PATH, vfr=True), Video(PATH), Video(PATH, reverse=True)):
            frames = 0
            def update():
                nonlocal frames
                if v.update():
                    frames += 1
            while_loop(lambda: v.active, update, 8)
            self.assertEqual(frames, 5)
            v.close()

    # tests correct errors are raised when given bad input paths
    def test_open_video(self):
        self.assertRaises(OpenCVError, lambda: Video("resources\\fake.txt"))
        self.assertRaises(FileNotFoundError, lambda: Video("badpath"))

    # tests get position accuracy
    def test_get_pos(self):
        v = Video(VIDEO_PATH)
        while_loop(lambda: v.get_pos() == 0.0, v.update, 2)
        excess = v.get_pos()
        t = time.time()
        timed_loop(5, v.update)
        pos = v.get_pos()
        t = time.time() - t
        self.assertTrue(abs(pos - excess - t) <= 0.05)

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

    # tests pyav dependency message
    def test_imageio_needs_pyav(self):
        # mocks away av
        dict_ = {key: None for key in sys.modules.keys() if key.startswith("av.")}
        dict_.update({"av": None})
        with unittest.mock.patch.dict("sys.modules", dict_):
            with self.assertRaises(ImportError) as context:
                Video("resources\\clip.mp4", reader=READER_IMAGEIO).preview()

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
        while_loop(lambda: not v.update(), lambda: None, 5, 0)

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

        with unittest.mock.patch("pyvidplayer2.video.PYAUDIO", 0):
            self.assertRaises(ModuleNotFoundError, Video, VIDEO_PATH)

            # should be fine
            Video(VIDEO_PATH, use_pygame_audio=True).close()

        with unittest.mock.patch("pyvidplayer2.video.PYGAME", 0):
            with self.assertRaises(ModuleNotFoundError):
                Video(VIDEO_PATH, use_pygame_audio=True)

            # should be fine
            Video(VIDEO_PATH, use_pygame_audio=False).close()

    # tests that different types of videos can be opened in reverse
    def test_reverse(self):
        PATH = "resources\\clip.mp4"

        for vfr in (True, False):
            v = Video(PATH, reverse=True, vfr=vfr)
            for i, frame in enumerate(v):
                self.assertTrue(check_same_frames(frame, v._preloaded_frames[v.frame_count - i - 1]))
            v.close()
        for reader in (READER_DECORD, READER_IMAGEIO):
            with open(PATH, "rb") as f:
                v = Video(f.read(), reverse=True, reader=reader)
                for i, frame in enumerate(v):
                    self.assertTrue(check_same_frames(frame, v._preloaded_frames[v.frame_count - i - 1]))
                v.close()

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
        self.assertEqual(VER, pyvidplayer2.__version__)
        self.assertEqual(VER, get_version_info()["pyvidplayer2"])

    # tests that the correct pts are extracted for vfr videos
    def test_get_timestamps(self):
        v = Video(VIDEO_PATH, vfr=True)
        self.assertEqual(v.timestamps[:10], [0.0, 0.041708, 0.083417, 0.125125, 0.166833, 0.208542, 0.25025, 0.291958,
                                        0.333667, 0.375375])
        self.assertEqual(v.timestamps[-10:], [66.858458, 66.900167,
                                        66.941875, 66.983583, 67.025292, 67.067, 67.108708, 67.150417, 67.192125,
                                        67.233833])
        v.close()

    # test __str__ from bytes
    def test_bytes_str(self):
        with open(VIDEO_PATH, "rb") as f:
            v = Video(f.read())
            self.assertEqual("<VideoPygame(path=)>", str(v))
            v.close()

    # tests _convert_seconds method built into the ffmpeg reader
    def test_ffmpeg_reader_convert_seconds(self):
        v = Video(VIDEO_PATH, reader=READER_FFMPEG)
        ffmpeg_reader = v._vid

        self.assertEqual(ffmpeg_reader._convert_seconds(7200), v._convert_seconds(7200))
        self.assertEqual(ffmpeg_reader._convert_seconds(7325), v._convert_seconds(7325))
        self.assertEqual(ffmpeg_reader._convert_seconds(125), v._convert_seconds(125))
        self.assertEqual(ffmpeg_reader._convert_seconds(59), v._convert_seconds(59))
        self.assertEqual(ffmpeg_reader._convert_seconds(7325.9), v._convert_seconds(7325.9))
        self.assertEqual(ffmpeg_reader._convert_seconds(0), v._convert_seconds(0))
        self.assertEqual(ffmpeg_reader._convert_seconds(90061.5), v._convert_seconds(90061.5))
        self.assertEqual(ffmpeg_reader._convert_seconds(-3665), v._convert_seconds(-3665))
        self.assertEqual(ffmpeg_reader._convert_seconds(4.98), v._convert_seconds(4.98))
        self.assertEqual(ffmpeg_reader._convert_seconds(4.98881), v._convert_seconds(4.98881))
        self.assertEqual(ffmpeg_reader._convert_seconds(12.1280937198881), v._convert_seconds(12.1280937198881))


        v.close()

    # test to ensure each reader behaves the same
    def test_readers(self):
        # lossless video to ensure read frames are the same
        PATH = "resources\\test.mp4"

        v1 = Video(PATH, reader=READER_OPENCV)
        v2 = Video(PATH, reader=READER_FFMPEG)
        v3 = Video(PATH, reader=READER_DECORD)
        v4 = Video(PATH, reader=READER_IMAGEIO)

        cv_reader = v1._vid
        ffmpeg_reader = v2._vid
        decord_reader = v3._vid
        iio_reader = v4._vid

        self.assertTrue(cv_reader.isOpened())
        self.assertTrue(ffmpeg_reader.isOpened())
        self.assertTrue(decord_reader.isOpened())
        self.assertTrue(iio_reader.isOpened())

        # test read frames are the same
        for i in range(10):
            self.assertTrue(check_same_frames(cv_reader.read()[1], ffmpeg_reader.read()[1]))
            self.assertTrue(check_same_frames(decord_reader.read()[1], iio_reader.read()[1]))
        for i in range(5):
            rgb_frame = decord_reader.read()[1]
            bgr_frame = ffmpeg_reader.read()[1]
            self.assertTrue(check_same_frames(rgb_frame[...,::-1], bgr_frame))

        # test seeking is the same
        cv_reader.seek(0)
        ffmpeg_reader.seek(0)
        decord_reader.seek(0)
        iio_reader.seek(0)

        self.assertEqual(cv_reader.frame, 0)
        self.assertEqual(ffmpeg_reader.frame, 0)
        self.assertEqual(decord_reader.frame, 0)
        self.assertEqual(iio_reader.frame, 0)

        for i in range(10):
            self.assertTrue(check_same_frames(cv_reader.read()[1], ffmpeg_reader.read()[1]))
            self.assertTrue(check_same_frames(decord_reader.read()[1], iio_reader.read()[1]))
        for i in range(5):
            rgb_frame = decord_reader.read()[1]
            bgr_frame = ffmpeg_reader.read()[1]
            self.assertTrue(check_same_frames(rgb_frame[...,::-1], bgr_frame))

        # tests has_frame is the same
        cv_reader.seek(v1.frame_count - 1)
        ffmpeg_reader.seek(v1.frame_count - 1)
        decord_reader.seek(v1.frame_count - 1)
        iio_reader.seek(v1.frame_count - 1)

        cv_reader.read()
        ffmpeg_reader.read()
        decord_reader.read()
        iio_reader.read()

        self.assertFalse(cv_reader.read()[0])
        self.assertFalse(ffmpeg_reader.read()[0])
        self.assertFalse(decord_reader.read()[0])
        self.assertFalse(iio_reader.read()[0])

        # test close
        cv_reader.release()
        ffmpeg_reader.release()
        decord_reader.release()
        iio_reader.release()

        v1.close()
        v2.close()
        v3.close()
        v4.close()

        self.assertFalse(cv_reader.isOpened())
        # non cv readers default to True for isOpened()
        self.assertTrue(ffmpeg_reader.isOpened())
        self.assertTrue(decord_reader.isOpened())
        self.assertTrue(iio_reader.isOpened())

    # tests that each video has its correct colour format
    def test_colour_format(self):
        v = Video(VIDEO_PATH, reader=READER_DECORD)
        self.assertEqual(v.colour_format, "RGB")
        v.close()
        v = Video(VIDEO_PATH, reader=READER_IMAGEIO)
        self.assertEqual(v.colour_format, "RGB")
        v.close()
        v = Video(VIDEO_PATH, reader=READER_OPENCV)
        self.assertEqual(v.colour_format, "BGR")
        v.close()
        v = Video(VIDEO_PATH, reader=READER_FFMPEG)
        self.assertEqual(v.colour_format, "BGR")
        v.close()

    # tests that each video object has the correct amount of parameters
    # here to ensure that new parameters are added to each video object
    def test_parameters(self):
        # test each graphics library with exact number of arguments

        v = Video(VIDEO_PATH, 10, 1, 1, None, PostProcessing.none, "linear", False, False, False, 1, False, 1080, False, 0, False, "en", None, READER_AUTO)
        v.close()
        for videoClass in (VideoTkinter, VideoPyglet, VideoPyQT, VideoRaylib):
            v = videoClass(VIDEO_PATH, 10, 1, 1, PostProcessing.none, "linear", False, False, False, 1, False, 1080, False,
                      0, False, "en", None, READER_AUTO)
            v.close()

        with self.assertRaises(TypeError):
            Video(VIDEO_PATH, 10, 1, 1, None, PostProcessing.none, "linear", False, False, False, 1, False, 1080, False, 0, False, "en", None, READER_AUTO, "extra_arg")

        for videoClass in (VideoTkinter, VideoPyglet, VideoPyQT, VideoRaylib, VideoPySide):
            with self.assertRaises(TypeError):
                videoClass(VIDEO_PATH, 10, 1, 1, PostProcessing.none, "linear", False, False, False, 1, False, 1080, False,
                          0, False, "en", None, READER_AUTO, "extra_arg")

    # tests that each backend can be forced
    def test_force_readers(self):
        v = Video(VIDEO_PATH, reader=READER_DECORD)
        self.assertEqual(type(v._vid).__name__, "DecordReader")
        v.close()
        v = Video(VIDEO_PATH, reader=READER_IMAGEIO)
        self.assertEqual(type(v._vid).__name__, "IIOReader")
        v.close()
        v = Video(VIDEO_PATH, reader=READER_OPENCV)
        self.assertEqual(type(v._vid).__name__, "CVReader")
        v.close()
        v = Video(VIDEO_PATH, reader=READER_FFMPEG)
        self.assertEqual(type(v._vid).__name__, "FFMPEGReader")
        v.close()

    # tests automatic selection of readers
    def test_auto_readers(self):
        v = Video(VIDEO_PATH)
        self.assertEqual(type(v._vid).__name__, "CVReader")
        v.close()

        with unittest.mock.patch("pyvidplayer2.video.CV", 0):
            v = Video(VIDEO_PATH)
            self.assertEqual(type(v._vid).__name__, "DecordReader")
            v.close()

            with self.assertRaises(ModuleNotFoundError):
                Video(VIDEO_PATH, reader=READER_OPENCV)

            with unittest.mock.patch("pyvidplayer2.video.DECORD", 0):
                v = Video(VIDEO_PATH)
                self.assertEqual(type(v._vid).__name__, "FFMPEGReader")
                v.close()

                with self.assertRaises(ModuleNotFoundError):
                    Video(VIDEO_PATH, reader=READER_DECORD)

                with unittest.mock.patch("pyvidplayer2.video.IIO", 0):
                    v = Video(VIDEO_PATH)
                    self.assertEqual(type(v._vid).__name__, "FFMPEGReader")
                    v.close()

                    with self.assertRaises(ModuleNotFoundError):
                        Video(VIDEO_PATH, reader=READER_IMAGEIO)

            with unittest.mock.patch("pyvidplayer2.video.IIO", 0):
                v = Video(VIDEO_PATH)
                self.assertEqual(type(v._vid).__name__, "DecordReader")
                v.close()

    # tests forced and auto selection of readers for reading from memory
    def test_byte_readers(self):
        with open(VIDEO_PATH, "rb") as f:
            bytes_ = f.read()

            v = Video(bytes_, as_bytes=True, reader=READER_AUTO)
            v.close()
            v = Video(bytes_, as_bytes=True, reader=READER_DECORD)
            v.close()
            v = Video(bytes_, as_bytes=True, reader=READER_IMAGEIO)
            v.close()

            with self.assertRaises(ValueError):
                Video(bytes_, as_bytes=True, reader=READER_FFMPEG)
            with self.assertRaises(ValueError):
                Video(bytes_, as_bytes=True, reader=READER_OPENCV)

            v = Video(bytes_, as_bytes=True)
            self.assertEqual(type(v._vid).__name__, "DecordReader")
            v.close()

            with unittest.mock.patch("pyvidplayer2.video.DECORD", 0):
                v = Video(bytes_, as_bytes=True)
                self.assertEqual(type(v._vid).__name__, "IIOReader")
                v.close()

                with unittest.mock.patch("pyvidplayer2.video.IIO", 0):
                    with self.assertRaises(ValueError) as context:
                        Video(bytes_, as_bytes=True)
                    self.assertEqual(str(context.exception), "Only READER_DECORD and READER_IMAGEIO is supported for reading from memory.")

                    with unittest.mock.patch("pyvidplayer2.video.DECORD", 1):
                        v = Video(bytes_, as_bytes=True)
                        self.assertEqual(type(v._vid).__name__, "DecordReader")
                        v.close()

    def test_random_read(self):
        for file in PATHS:
            for reader in (READER_FFMPEG,):
                Video(file, reader=reader).close()

    # tests forcing reader to be ffmpeg - similar to youtube equivalent
    def test_force_ffmpeg(self):
        for reader in (READER_DECORD, READER_IMAGEIO):
            v = Video(VIDEO_PATH, reader=reader)
            self.assertEqual(v.colour_format, "RGB")
            timed_loop(1, v.update)
            v._force_ffmpeg_reader()
            self.assertEqual(v.colour_format, "BGR")
            self.assertEqual(type(v._vid).__name__, "FFMPEGReader")
            self.assertEqual(v._vid.frame, v.frame)
            timed_loop(1, v.update)
            v.close()


if __name__ == "__main__":
    unittest.main()
