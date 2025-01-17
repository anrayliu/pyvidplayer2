import unittest
import time
from pyvidplayer2 import *
from test_video import while_loop, timed_loop, check_same_frames, VIDEO_PATH


class TestWebcam(unittest.TestCase):
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

    # tests __str__
    def test_str_magic_method(self):
        w = Webcam()
        self.assertEqual("<Webcam(fps=30)>", str(w))
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
    # can only succeed if you have a 60 fps webcam
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

    # tests the set_interp method
    def test_set_interp(self):
        w = Webcam(interp="linear")
        self.assertEqual(w.interp, cv2.INTER_LINEAR)
        w.close()
        w = Webcam(interp="cubic")
        self.assertEqual(w.interp, cv2.INTER_CUBIC)
        w.close()
        w = Webcam(interp="area")
        self.assertEqual(w.interp, cv2.INTER_AREA)
        w.close()
        w = Webcam(interp="lanczos4")
        self.assertEqual(w.interp, cv2.INTER_LANCZOS4)
        w.close()
        w = Webcam(interp="nearest")
        self.assertEqual(w.interp, cv2.INTER_NEAREST)

        w.set_interp("linear")
        self.assertEqual(w.interp, cv2.INTER_LINEAR)
        w.set_interp("cubic")
        self.assertEqual(w.interp, cv2.INTER_CUBIC)
        w.set_interp("area")
        self.assertEqual(w.interp, cv2.INTER_AREA)
        w.set_interp("lanczos4")
        self.assertEqual(w.interp, cv2.INTER_LANCZOS4)
        w.set_interp("nearest")
        self.assertEqual(w.interp, cv2.INTER_NEAREST)

        w.set_interp(cv2.INTER_LINEAR)
        self.assertEqual(w.interp, cv2.INTER_LINEAR)
        w.set_interp(cv2.INTER_CUBIC)
        self.assertEqual(w.interp, cv2.INTER_CUBIC)
        w.set_interp(cv2.INTER_AREA)
        self.assertEqual(w.interp, cv2.INTER_AREA)
        w.set_interp(cv2.INTER_LANCZOS4)
        self.assertEqual(w.interp, cv2.INTER_LANCZOS4)
        w.set_interp(cv2.INTER_NEAREST)
        self.assertEqual(w.interp, cv2.INTER_NEAREST)

        self.assertRaises(ValueError, w.set_interp, "unrecognized interp")

        w.close()

    # tests that produced resampled images are the same that a video class produces
    def test_resampling(self):
        v = Video(VIDEO_PATH)
        original_frame = next(v)

        w = Webcam()

        SIZES = ((426, 240), (640, 360), (854, 480), (1280, 720), (1920, 1080), (2560, 1440), (3840, 2160), (7680, 4320))

        for size in SIZES:
            for flag in (cv2.INTER_LINEAR, cv2.INTER_NEAREST, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4, cv2.INTER_AREA):
                new_frame = v._resize_frame(original_frame, size, flag, False)
                webcam_resized = w._resize_frame(original_frame, size, flag)
                self.assertTrue(check_same_frames(new_frame, webcam_resized))

        v.close()
        w.close()

if __name__ == "__main__":
    unittest.main()