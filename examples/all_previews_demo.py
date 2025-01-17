'''
This shows off each graphics api and their respective preview methods
Must install pygame, tkinter, pyglet, and pyqt6, pyside, and raylib for this example
'''


from pyvidplayer2 import Video, VideoTkinter, VideoPyglet, VideoPyQT, VideoPySide, VideoRaylib

PATH = r"resources\trailer1.mp4"

# previews are just a quick demonstration of the video
# you can test different video settings (speed, reverse, youtube, etc)
# but remember that everything shown in a preview can also be integrated
# into your chosen graphics library (see demos)

Video(PATH).preview()
VideoTkinter(PATH).preview()
VideoPyglet(PATH).preview()
VideoPyQT(PATH).preview()
VideoPySide(PATH).preview()
VideoRaylib(PATH).preview()
