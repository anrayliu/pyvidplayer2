from pyvidplayer2 import Video, VideoTkinter, VideoPyglet

PATH = r"resources\trailer.mp4"

# accepts pygame, pyglet, and tkinter to render graphics

Video(PATH).preview()

VideoPyglet(PATH).preview()

VideoTkinter(PATH).preview()