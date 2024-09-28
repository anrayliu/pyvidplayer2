'''
This shows off each graphics api and their respective preview methods
Must install pygame, tkinter, pyglet, and pyqt6 for this example
'''


from pyvidplayer2 import Video, VideoTkinter, VideoPyglet, VideoPyQT, VideoPySide

PATH = r"resources\trailer1.mp4"

Video(PATH).preview()
VideoTkinter(PATH).preview()
VideoPyglet(PATH).preview()
VideoPyQT(PATH).preview()
VideoPySide(PATH).preview()