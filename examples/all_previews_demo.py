'''
This shows off each graphics api and their respective preview methods
'''

# Sample videos can be found here:
# https://github.com/anrayliu/pyvidplayer2-test-resources/tree/main/resources


from pyvidplayer2 import (Video, VideoPyglet, VideoPyQT, VideoPySide,
                          VideoRaylib, VideoTkinter, VideoWx)

# previews are just a quick demonstration of the video
# you can test different video settings (speed, reverse, youtube, etc)
# but remember that everything shown in a preview can also be integrated
# into your chosen graphics library (see demos)

PATH = r"resources\trailer1.mp4"

# for Pygame and Pygame CE
Video(PATH).preview()

# enables fps display in preview
# Video(PATH, speed=2, no_audio=True).preview(True)

# VideoTkinter(PATH).preview()

# VideoPyglet(PATH).preview()

# VideoPyQT(PATH).preview()

# VideoPySide(PATH).preview()

# VideoRaylib(PATH).preview()

# VideoWx(PATH).preview()
