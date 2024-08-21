'''
This example shows how filters can stack, speeding up and reversing the video
'''

from pyvidplayer2 import Video

v = Video(r"resources\birds.avi", reverse=True, speed=3).preview()
