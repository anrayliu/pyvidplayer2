import time
import unittest
from threading import Thread
import unittest.mock
import yt_dlp
import random
from test_subtitles import SUBS
from test_video import while_loop, timed_loop, check_same_frames
from pyvidplayer2 import *


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


YOUTUBE_PATH = "https://www.youtube.com/watch?v=K8PoK3533es&t=3s"


class TestYoutubeVideo(unittest.TestCase):
    # tests that each video is opened properly
    def test_metadata(self):
        v = Video(YOUTUBE_PATH, youtube=True)
        self.assertTrue(v.path.startswith("https"))
        self.assertTrue(v._audio_path.startswith("https"))
        self.assertEqual(v.name, "The EASIEST Way to Play Videos in Pygame/Python!")
        self.assertEqual(v.ext, ".webm")
        self.assertEqual(v.duration, 69.36666666666666)
        self.assertEqual(v.frame_count, 2081)
        self.assertEqual(v.frame_rate, 30.0)
        self.assertEqual(v.original_size, (1280, 720))
        self.assertEqual(v.current_size, (1280, 720))
        self.assertEqual(v.aspect_ratio, 1.7777777777777777)
        self.assertEqual(type(v._vid).__name__, "CVReader")
        v.close()
        time.sleep(0.1)

    # tests youtube max_res parameter
    def test_max_resolution(self):
        for res in (144, 360, 720, 1080):
            v = Video(YOUTUBE_PATH, youtube=True, max_res=res)
            self.assertEqual(v.current_size[1], res)
            v.close()
            time.sleep(0.1)  # prevents spamming youtube

    # test opens the first 5 trending youtube videos
    def test_youtube(self):
        for url in get_youtube_urls():
            v = Video(url, youtube=True)
            self.assertTrue(v._audio_path.startswith("https"))
            self.assertTrue(v.path.startswith("https"))
            while_loop(lambda: v.get_pos() < 1, v.update, 10)
            v.close()
            time.sleep(0.1)

    # test that youtube chunk settings are checked
    def test_youtube_settings(self):
        v = Video(YOUTUBE_PATH, youtube=True, chunk_size=30, max_threads=3, max_chunks=3)
        self.assertEqual(v.chunk_size, 60)
        self.assertEqual(v.max_threads, 1)
        self.assertEqual(v.max_chunks, 3)
        v.close()
        time.sleep(0.1)

    # tests opening a youtube video with bad paths
    def test_open_youtube(self):
        with self.assertRaises(YTDLPError) as context:
            Video("resources\\trailer1.mp4", youtube=True)
        self.assertEqual(str(context.exception),
                         "yt-dlp could not open video. Please ensure the URL is a valid Youtube video.")
        time.sleep(0.1)

        with self.assertRaises(YTDLPError) as context:
            Video(YOUTUBE_PATH, youtube=True, max_res=0)
        self.assertEqual(str(context.exception), "Could not find requested resolution.")
        time.sleep(0.1)

        with self.assertRaises(YTDLPError) as context:
            Video("https://www.youtube.com/watch?v=thisvideodoesnotexistauwdhoiawdhoiawhdoih", youtube=True)
        self.assertEqual(str(context.exception),
                         "yt-dlp could not open video. Please ensure the URL is a valid Youtube video.")
        time.sleep(0.1)

    # tests that youtube videos do not hang when close is called
    def test_hanging(self):
        v = Video(YOUTUBE_PATH, youtube=True, max_threads=10, max_chunks=10)
        t = time.time()
        v.close()
        self.assertLess(time.time() - t, 0.1)
        time.sleep(0.1)

    # tests that youtube videos can be played in reverse
    def test_reverse(self):
        v = Video(YOUTUBE_PATH, reverse=True, youtube=True)
        for i, frame in enumerate(v):
            self.assertTrue(check_same_frames(frame, v._preloaded_frames[v.frame_count - i - 1]))
        v.close()
        time.sleep(0.1)

    # tests for errors for unsupported youtube links
    def test_bad_youtube_links(self):
        for url in ("https://www.youtube.com/@joewoobie1155", "https://www.youtube.com/channel/UCY3Rgenpuy4cY79eGk6DmuA", "https://www.youtube.com/", "https://www.youtube.com/shorts"):
            with self.assertRaises(YTDLPError):
                Video(url, youtube=True).close()
            time.sleep(0.1)

    # tests that nothing crashes when selecting different languages with Youtube
    def test_youtube_language_tracks(self):
        for lang in (None, "en-US", "fr-FR", "es-US", "it", "pt-BR", "de-DE", "badcode"):
            v = Video("https://www.youtube.com/watch?v=v4H2fTgHGuc", youtube=True, pref_lang=lang)
            timed_loop(3, v.update)
            v.close()
            time.sleep(0.1)

    # tests appropriate error messages when opening subtitles
    def test_open_subtitles(self):
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
        time.sleep(0.1)

    # tests __str__
    def test_str_magic_method(self):
        v = Video(YOUTUBE_PATH, youtube=True)
        self.assertEqual("<VideoPygame(path=)>", str(v))
        v.close()
        time.sleep(0.1)

    # tests that subtitles are properly read and displayed
    def test_subtitles(self):
        # running video in x5 to speed up test
        v = Video("https://www.youtube.com/watch?v=HurjfO_TDlQ", subs=Subtitles("https://www.youtube.com/watch?v=HurjfO_TDlQ", youtube=True, pref_lang="en-US"), speed=5, youtube=True)

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
        v.close()
        time.sleep(0.1)

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
        time.sleep(0.1)

    # tests forcing reader to be ffmepg
    def test_force_ffmpeg(self):
        v = Video(YOUTUBE_PATH, youtube=True)
        timed_loop(2, v.update)
        v._force_ffmpeg_reader()
        self.assertEqual(type(v._vid).__name__, "FFMPEGReader")
        self.assertEqual(v._vid.frame, v.frame)
        timed_loop(2, v.update)
        v.close()

    # tests forced and auto selection of readers for youtube
    def test_youtube_readers(self):
        v = Video(YOUTUBE_PATH, youtube=True)
        self.assertEqual(type(v._vid).__name__, "CVReader")

        # using _get_best_reader instead of creating Video objects
        # to reduce network spam

        # test for exceptions here
        # youtube = True, as_bytes = False, reader = READER_AUTO
        v._get_best_reader( True, False, READER_AUTO)
        v._get_best_reader( True, False, READER_OPENCV)

        with self.assertRaises(ValueError):
            v._get_best_reader(True, False, READER_FFMPEG)
        with self.assertRaises(ValueError):
            v._get_best_reader(True, False, READER_IMAGEIO)
        with self.assertRaises(ValueError):
            v._get_best_reader(True, False, READER_IMAGEIO)

        with unittest.mock.patch("pyvidplayer2.video.CV", 0):
            with self.assertRaises(ValueError) as context:
                Video(YOUTUBE_PATH, youtube=True)
            self.assertEqual(str(context.exception),
                             "Only READER_OPENCV is supported for Youtube videos.")

        v.close()


if __name__ == "__main__":
    unittest.main()