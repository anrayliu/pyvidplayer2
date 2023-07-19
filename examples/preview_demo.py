from pyvidplayer2 import Video, VideoTkinter, VideoPyglet

PATH = "demos\\vids\\walter.mp4"

Video(PATH).preview()

VideoPyglet(PATH).preview()

VideoTkinter(PATH).preview()