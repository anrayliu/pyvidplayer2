import random
import time
from threading import Thread
from test_video import VIDEO_PATH, while_loop, timed_loop, check_same_frames
import unittest
from pyvidplayer2 import *


class TestVideoPlayer(unittest.TestCase):
    # tests that a video can be played entirely in a video player
    def test_full_player(self):
        v = Video("resources\\clip.mp4")
        vp = VideoPlayer(v, (0, 0, *v.original_size))
        while_loop(lambda: v.active, vp.update, 10)
        vp.close()
        self.assertTrue(vp.closed)

    # tests zoom out and zoom to fill
    def test_zoom(self):
        for i in range(100):
            pos = (random.randint(0, 2000), random.randint(0, 2000))
            size = (random.randint(100, 2000), random.randint(100, 2000))
            vp = VideoPlayer(Video(VIDEO_PATH), (*pos, *size))

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

            vp.close()

    # tests default video player
    def test_open_video_player(self):
        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, *v.original_size))
        self.assertIs(vp.video, v)
        self.assertIs(vp.get_video(), v)
        self.assertEqual(vp.vid_rect, pygame.Rect(0, 0, v.original_size[0], v.original_size[1]))
        self.assertEqual(vp.frame_rect, pygame.Rect(0, 0, v.original_size[0], v.original_size[1]))
        self.assertFalse(vp.interactable)
        self.assertFalse(vp.loop)
        self.assertEqual(vp.preview_thumbnails, 0)
        self.assertEqual(vp._font.get_height(), 12) # point size 10 should result in 12 height
        self.assertEqual(vp._font.name, "Arial")
        vp.close()

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

    # tests video player with context manager
    def test_context_manager(self):
        with VideoPlayer(Video(VIDEO_PATH), (0, 0, 1280, 720)) as vp:
            self.assertFalse(vp.closed)
            self.assertFalse(vp.get_video().closed)
        self.assertTrue(vp.closed)
        self.assertTrue(vp.get_video().closed)

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
        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, *v.original_size))

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

        vp.close()

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
        vp = VideoPlayer(Video(VIDEO_PATH), (0, 0, 1280, 720))

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

        vp.close()

    # tests _convert_seconds for videoplayer
    def test_video_player_convert_seconds(self):
        vp = VideoPlayer(Video(VIDEO_PATH), (0, 0, 1280, 720))

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

        self.assertEqual(vp._convert_seconds(4.98), "0:0:4")
        self.assertEqual(vp._convert_seconds(4.98881), "0:0:4")
        self.assertEqual(vp._convert_seconds(12.1280937198881), "0:0:12")

        vp.close()

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

    # tests __str__
    def test_str_magic_method(self):
        vp = VideoPlayer(Video(VIDEO_PATH), (0, 0, 1280, 720))
        self.assertEqual("<VideoPlayer(path=resources\\trailer1.mp4)>", str(vp))
        vp.close()

    # tests that previews behave correctly
    def test_preview(self):
        v = Video(VIDEO_PATH)
        vp = VideoPlayer(v, (0, 0, 1280, 720))
        v.seek(v.duration)
        thread = Thread(target=lambda: vp.preview())
        thread.start()
        time.sleep(1)
        self.assertFalse(thread.is_alive())
        self.assertTrue(vp.closed)


if __name__ == "__main__":
    unittest.main()
