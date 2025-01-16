import unittest
import random
from pyvidplayer2 import *
from test_video import while_loop, timed_loop, check_same_frames


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


class TestSubtitles(unittest.TestCase):
    def test_str_magic_method(self):
        s = Subtitles("resources\\subs1.srt")
        self.assertEqual("<Subtitles(path=resources\\subs1.srt)>", str(s))

    # tests that subtitle tracks from videos can also be read
    def test_embedded_subtitles(self):
        s = Subtitles("resources/wSubs.mp4", track_index=0)

        self.assertEqual(s.track_index, 0)

        for i in range(len(SUBS)):
            s._get_next()
            self.assertEqual(s.start, SUBS[i][0])
            self.assertEqual(s.end, SUBS[i][1])
            self.assertEqual(s.text, SUBS[i][2])

    # tests minor features of the subtitles for crashes
    def test_additional_tests(self):
        s1 = Subtitles("resources\\subs1.srt", colour="blue", highlight="red",
                       font=pygame.font.SysFont("arial", 35), offset=70, delay=-1)
        s2 = Subtitles("resources\\subs2.srt", colour=pygame.Color("pink"), highlight=(129, 12, 31, 128),
                       font=pygame.font.SysFont("arial", 20))
        s3 = Subtitles("resources\\subs2.srt", colour=(123, 13, 52, 128), highlight=(4, 131, 141, 200),
                       font=pygame.font.SysFont("arial", 40), delay=1)
        s4 = Subtitles("resources\\subs1.srt", delay=10000)
        font = pygame.font.SysFont("arial", 10)
        self.assertRaises(ValueError, lambda: s1.set_font(pygame.font.Font))
        s1.set_font(font)
        self.assertIs(font, s1.get_font())

    # tests opening subtitle files with different encodings
    def test_subtitle_encoding(self):
        self.assertRaises(SubtitleError, lambda: Subtitles("resources\\utf16.srt"))
        Subtitles("resources\\utf16.srt", encoding="utf16")

    # tests __str__
    def test_str_magic_method(self):
        s = Subtitles("resources\\subs1.srt")
        self.assertEqual(str(s), "<Subtitles(path=resources\\subs1.srt)>")

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


    # tests that subtitles are properly read and displayed
    def test_subtitles(self):
        # running video in x6 to speed up test
        v = Video("resources\\trailer1.mp4", subs=Subtitles("resources\\subs1.srt"), speed=6)

        def check_subs():
            v.update()

            timestamp = v._update_time
            # skip when frame has not been rendered yet
            if v.frame_data is None:
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

        # test that seeking works for subtitles
        for i in range(3):
            v.seek(random.uniform(0, v.duration), relative=False)
            v.play()
            timed_loop(1, v.update)

        v.close()


if __name__ == "__main__":
    unittest.main()
