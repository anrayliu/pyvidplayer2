'''
This example shows that each type of video uses their respective
graphics API to render previews.
'''


from pyvidplayer2 import Video, VideoTkinter, VideoPyglet

PATH = r"resources\trailer1.mp4"

Video(PATH).preview()

VideoTkinter(PATH).preview()

VideoPyglet(PATH).preview()
