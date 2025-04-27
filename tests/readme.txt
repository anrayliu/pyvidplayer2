Full unit tests for pyvidplayer2 v0.9.26

Requires the resources folder which contains all the test videos
Download the videos here: https://github.com/anrayliu/pyvidplayer2-test-resources
Requires all optional dependencies

Currently failing tests:

test_detect_as_bytes - fails because ffprobe really struggles to extract information from these types of videos
test_frame_counts - fails because frame count extraction is currently unreliable
test_many_video_tracks - fails because decord does not read from the first video track

Note: Some tests can be inconsistent, depending on your computer specs
My 5600x has no issues, while my 7530U sometimes struggles