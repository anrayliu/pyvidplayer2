import math
import random
import unittest
from pyvidplayer2 import *
import os
import time
import cv2


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
        func()

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


# readers
# different files


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

        for func in (PostProcessing.blur, PostProcessing.sharpen, PostProcessing.greyscale, PostProcessing.noise, PostProcessing.letterbox, PostProcessing.cel_shading):
            v2.set_post_func(func)
            self.assertFalse(check_same_frames(next(v1), next(v2)))

        v1.close()
        v2.close()

    def test_metadata(self):
        v = Video("resources\\trailer1.mp4")
        self.assertEqual(v.path, "resources\\trailer1.mp4")
        self.assertEqual(v.name, "trailer1")
        self.assertEqual(v.ext, ".mp4")
        self.assertEqual(v.duration, 67.27554166666665)
        self.assertEqual(v.frame_count, 1613)
        self.assertEqual(v.frame_rate, 23.976023976023978)
        self.assertEqual(v.original_size, (1280, 720))
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
            v = Video(file)
            if v.name in ("manya",):
                v.close()
                continue
            self.assertFalse(v.as_bytes)
            v.close()
            with open(file, "rb") as f:
                v = Video(f.read())
                self.assertTrue(v.as_bytes)
                self.assertEqual(v._audio_path, "-")
                v.close()

    # tests seeking, requires an accurate frame_count attribute
    def test_seeking(self):
        for file in PATHS:
            v = Video(file)
            v.probe()

            if v.name in ("hdr",):
                v.close()
                continue

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
            self.assertEqual(v.get_pos(), round(v.frame_delay * FRAME, 2))
            self.assertEqual(v.frame, FRAME)

            new_frame = next(v)

            self.assertTrue(check_same_frames(original_frame, new_frame))

            # testing relative frame seek
            v.seek_frame(-FRAME, relative=True)
            self.assertEqual(v.get_pos(), round(v.frame_delay, 2))
            self.assertEqual(v.frame, 1)

            # testing lower bound
            v.seek(-1, relative=False)
            self.assertEqual(v.get_pos(), 0.0)
            self.assertEqual(v.frame, 0)

            # testing upper bound
            v.seek(v.duration)

            # should never raise a stop iteration exception
            next(v)
            v.seek(v.duration)

            self.assertEqual(v.get_pos(), math.floor(v.duration * 100) / 100.0)
            self.assertEqual(v.frame, v.frame_count - 1)

            v.seek_frame(v.frame_count)

            # should never raise a stop iteration exception
            next(v)
            v.seek_frame(v.frame_count)

            self.assertEqual(v.get_pos(), round(v.frame_delay * (v.frame_count - 1), 2))
            self.assertEqual(v.frame, v.frame_count - 1)

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
        v.seek(v.duration)
        v.update()
        self.assertTrue(v.active)
        v.stop()
        self.assertFalse(v.active)
        v.play()
        self.assertTrue(v.active)
        v.close()

    def test_stop(self):
        v = Video(VIDEO_PATH)
        timed_loop(1, lambda: v.update())
        v.stop()
        self.assertFalse(v.active)
        self.assertEqual(v.frame_data, None)
        self.assertEqual(v.frame_surf, None)
        self.assertFalse(v.paused)
        v.close()

    def test_set_speed_method(self):
        v = Video(VIDEO_PATH)
        self.assertRaises(DeprecationWarning, v.set_speed, 1.0)

    def test_preloaded_frames(self):
        v = Video("resources\\trailer1.mp4")
        v._preload_frames()
        for i, frame in enumerate(v):
            self.assertTrue(check_same_frames(v._preloaded_frames[i], frame))
        v.close()

    def test_frame_counts(self):
        for file in PATHS:
            v = Video(file)
            self.assertEqual(v.frame_count, v._get_real_frame_count())
            v.close()

    def test_mute(self):
        v = Video(VIDEO_PATH)
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
        v.unmute()
        self.assertFalse(v.muted)
        self.assertFalse(v._audio.muted)

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

    def test_probe(self):
        for file in PATHS:
            v = Video(file)
            v.probe()
            self.assertGreater(v.frame_count, 0)
            self.assertGreater(v.frame_rate, 0)
            self.assertGreater(v.duration, 0)

    def test_closed(self):
        v = Video(VIDEO_PATH)
        self.assertFalse(v.closed)
        self.assertFalse(v._audio.loaded)
        self.assertFalse(v._vid.released)
        timed_loop(5, lambda: v.update())
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

    def test_youtube(self):
        for url in get_youtube_urls():
            v = Video(url, youtube=True)
            self.assertTrue(v._audio_path.startswith("https"))
            self.assertTrue(v.path.startswith("https"))
            timed_loop(10, lambda: v.update())
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
        self.assertEqual(v.speed, 10)
        v.close()


# dependencies
# readers
# constantly opening new videos










    def test_parameters(self):
        v = Video("resources\\trailer1.mp4", chunk_size=1, max_threads=1, max_chunks=1, subs=None, post_process=PostProcessing.none,
                  interp="linear", use_pygame_audio=False, reverse=False, no_audio=False, speed=1.0, youtube=False, max_res=1080,
                  as_bytes=False, audio_track=0, vfr=False, pref_lang="en", audio_index=None)

        self.assertEqual(v.use_pygame_audio, False)
        self.assertEqual(v.reverse, False)
        self.assertEqual(v.no_audio, False)
        self.assertEqual(v.speed, 1.0)
        self.assertEqual(v.youtube, False)
        self.assertEqual(v.max_res, 1080)
        self.assertEqual(v.audio_track, 0)
        self.assertEqual(v.pref_lang, "en")
        self.assertEqual(v.audio_index, None)



if __name__ == "__main__":
    unittest.main()
