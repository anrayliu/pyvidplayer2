'''
This example shows how Video objects can be used in a context manager
'''

from pyvidplayer2 import Video 


with Video("resources\\trailer2.mp4") as video:
    video.preview()

# context managers will automatically call video.close() for you when done
