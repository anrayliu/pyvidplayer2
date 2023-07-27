'''
This is a quick example of integrating a video into a pyglet project
Double buffering is turned off to benefit from turning off force draw on the video
'''


import pyglet 
from pyvidplayer2 import VideoPyglet

video = VideoPyglet(r"resources\trailer1.mp4")

def update(dt):
    video.draw((0, 0), force_draw=False)
    if not video.active:
        win.close()

win = pyglet.window.Window(width=video.current_size[0], height=video.current_size[1], config=pyglet.gl.Config(double_buffer=False), caption=f"pyglet support demo")

pyglet.clock.schedule_interval(update, 1/60.0)

pyglet.app.run()
video.close()