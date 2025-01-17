'''
This is a quick example of integrating a video into a pyglet project
'''


import pyglet 
from pyvidplayer2 import VideoPyglet

video = VideoPyglet(r"resources\trailer1.mp4")

def update(dt):
    # unfortunately, I could not find a way to run force_draw=False without visual jitter,
    # even with double buffering turned off
    # I'd love to work with anyone more experienced in pyglet to find a way to optimize
    # this code more

    video.draw((0, 0), force_draw=True)
    if not video.active:
        win.close()

win = pyglet.window.Window(width=video.current_size[0], height=video.current_size[1], caption=f"pyglet support demo")

pyglet.clock.schedule_interval(update, 1/60.0)

pyglet.app.run()
video.close()
