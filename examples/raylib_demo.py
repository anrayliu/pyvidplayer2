'''
This is a quick example of integrating a video into a raylib project
'''

import pyray
from pyvidplayer2 import VideoRaylib

# 1. create video
video = VideoRaylib("resources\\trailer1.mp4")

# disables logs
pyray.set_trace_log_level(pyray.TraceLogLevel.LOG_NONE)

pyray.init_window(*video.original_size,f"raylib - {video.name}")
pyray.set_target_fps(60)

while not pyray.window_should_close() and video.active:
    pyray.begin_drawing()

    # 2. draw video onto window
    if video.draw((0, 0), force_draw=False):
        pyray.end_drawing()     # updates screen

pyray.close_window()

# 3. close video when done, also releases raylib textures
video.close()
