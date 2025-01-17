Full unit tests for pyvidplayer2 v0.9.25
Takes 10-15 minutes to complete all unit tests

Requires the resources folder which contains all the test videos
Download the videos here: https://github.com/anrayliu/pyvidplayer2-test-resources
Requires all optional dependencies

Currently failing tests:

test_detect_as_bytes - fails because ffprobe really struggles to extract information from these types of videos
test_frame_counts - fails because frame count extraction is currently unreliable
test_many_video_tracks - fails because decord does not read from the first video track
test_webcam_60_fps - should only fail if you don't have a 60 fps webcam

